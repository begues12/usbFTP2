import subprocess
from flask import Blueprint, jsonify, request
import os

storage_bp = Blueprint('storage', __name__)

@storage_bp.route('/create_usb_volume', methods=['POST'])
def create_usb_volume():
    try:
        # Obtener datos del formulario
        name = request.json.get('name')  # Nombre del volumen
        size = float(request.json.get('size'))  # Tamaño en GB

        if not name or not size:
            return jsonify({'error': 'El nombre y el tamaño son obligatorios'}), 400

        # Verificar el dispositivo principal (e.g., /dev/sda)
        device = "/dev/sda"  # Cambia esto si tu dispositivo principal es diferente
        result = subprocess.run(['lsblk', '-b', '-o', 'NAME,SIZE,MOUNTPOINT'], stdout=subprocess.PIPE, text=True)
        output = result.stdout

        # Calcular el inicio y fin de la nueva partición
        last_partition = None
        for line in output.splitlines()[1:]:
            parts = line.split()
            if len(parts) >= 3 and parts[0].startswith('sda'):
                last_partition = parts[0]

        if not last_partition:
            return jsonify({'error': 'No se encontró una partición válida en el dispositivo'}), 500

        # Obtener el tamaño total del dispositivo
        total_size = int([line.split()[1] for line in output.splitlines() if line.startswith('sda')][0])

        # Calcular el inicio y fin de la nueva partición
        used_size = sum(int(line.split()[1]) for line in output.splitlines() if line.startswith('sda') and len(line.split()) > 2)
        start_sector = used_size
        end_sector = start_sector + int(size * (1024 ** 3))  # Convertir GB a bytes

        if end_sector > total_size:
            return jsonify({'error': 'El tamaño solicitado excede el espacio disponible en el dispositivo'}), 400

        # Crear la nueva partición usando parted
        subprocess.run(['sudo', 'parted', device, 'mkpart', name, 'ext4', f'{start_sector}B', f'{end_sector}B'], check=True)

        # Formatear la partición como ext4
        partition_name = f"{device}{len(last_partition) + 1}"  # Asumimos que la nueva partición será la siguiente
        subprocess.run(['sudo', 'mkfs.ext4', partition_name], check=True)

        # Configurar el volumen USB para que sea usable
        mount_point = f"/mnt/{name}"
        subprocess.run(['sudo', 'mkdir', '-p', mount_point], check=True)
        subprocess.run(['sudo', 'mount', partition_name, mount_point], check=True)

        return jsonify({'message': f'Volumen USB "{name}" creado y montado en {mount_point} con éxito'}), 200

    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'Error al ejecutar un comando del sistema: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error inesperado: {str(e)}'}), 500
    
@storage_bp.route('/get_storage_info', methods=['GET'])
def get_storage_info():
    try:
        # Ejecutar el comando 'lsblk' para obtener información del dispositivo
        result = subprocess.run(['lsblk', '-b', '-o', 'NAME,SIZE,MOUNTPOINT'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout

        # Procesar la salida de lsblk
        partitions = []
        total_storage = 0
        system_storage = 0
        unallocated_storage = 0

        for line in output.splitlines()[1:]:  # Saltar la primera línea (encabezados)
            parts = line.split()
            if len(parts) < 2:
                continue

            name = parts[0]
            size = int(parts[1])  # Tamaño en bytes
            mountpoint = parts[2] if len(parts) > 2 else None

            # Si es el dispositivo principal (e.g., sda), obtener el tamaño total
            if not mountpoint and len(name) == 3:  # e.g., "sda"
                total_storage = size / (1024 ** 3)  # Convertir a GB
            elif mountpoint in ['/', '/boot', '/home']:
                # Clasificar como almacenamiento del sistema
                system_storage += size / (1024 ** 3)
            else:
                # Agregar partición a la lista
                partitions.append({
                    'name': mountpoint or f'/dev/{name}',
                    'size': round(size / (1024 ** 3), 2),
                    'type': 'ext4'  # Puedes ajustar esto según el sistema
                })

        # Calcular el espacio no asignado
        used_storage = system_storage + sum(partition['size'] for partition in partitions)
        unallocated_storage = total_storage - used_storage

        # Asegurarse de que no haya valores negativos
        unallocated_storage = max(unallocated_storage, 0)

        # Devolver los datos como JSON
        return jsonify({
            'partitions': partitions,
            'total_storage': round(total_storage, 2),
            'system_storage': round(system_storage, 2),
            'unallocated_storage': round(unallocated_storage, 2)
        })

    except Exception as e:
        return jsonify({'error': f'Error al obtener información del almacenamiento: {str(e)}'}), 500
    
# Ruta para crear una partición
@storage_bp.route('/create_partition', methods=['POST'])
def create_partition():
    try:
        # Depurar los datos recibidos
        print("Datos recibidos:", request.json)

        size = request.json.get('size')  # Tamaño de la partición en GB
        name = request.json.get('name')  # Nombre de la partición
        if not size or not name:
            return jsonify({'error': 'El tamaño y el nombre son obligatorios'}), 400

        # Crear la partición usando parted
        command = f"sudo parted /dev/sda mkpart {name} ext4 0% {size}GB"
        subprocess.run(command, shell=True, check=True)

        return jsonify({'message': 'Partición creada con éxito'}), 200
    except Exception as e:
        return jsonify({'error': f'Error al crear la partición: {str(e)}'}), 500
    
# Ruta para borrar una partición
@storage_bp.route('/delete_partition', methods=['POST'])
def delete_partition():
    try:
        name = request.json.get('name')  # Nombre de la partición
        if not name:
            return jsonify({'error': 'El nombre de la partición es obligatorio'}), 400

        # Borrar la partición usando parted
        command = f"sudo parted /dev/sda rm {name}"
        subprocess.run(command, shell=True, check=True)

        return jsonify({'message': 'Partición eliminada con éxito'}), 200
    except Exception as e:
        return jsonify({'error': f'Error al eliminar la partición: {str(e)}'}), 500


# Ruta para editar una partición (cambiar tamaño o nombre)
@storage_bp.route('/edit_partition', methods=['POST'])
def edit_partition():
    try:
        # Depurar los datos recibidos
        print("Datos recibidos:", request.json)

        name = request.json.get('name')  # Nombre completo del dispositivo
        partition_number = request.json.get('partition_number')  # Número de la partición
        size = float(request.json.get('size'))  # Nuevo tamaño en GB

        if not name or not partition_number or not size:
            return jsonify({'error': 'El nombre, el número de partición y el tamaño son obligatorios'}), 400

        # Cambiar el tamaño de la partición
        command_resize = f"sudo parted {name} resizepart {partition_number} {size}GB"
        result = subprocess.run(command_resize, shell=True, text=True, stderr=subprocess.PIPE)

        if result.returncode != 0:
            return jsonify({'error': f'Error al ejecutar el comando: {result.stderr.strip()}'}), 500

        return jsonify({'message': 'Partición editada con éxito'}), 200
    except Exception as e:
        return jsonify({'error': f'Error inesperado: {str(e)}'}), 500
            
# Ruta para reducir el tamaño de una partición
@storage_bp.route('/shrink_partition', methods=['POST'])
def shrink_partition():
    try:
        name = request.json.get('name')  # Nombre de la partición
        new_size = request.json.get('new_size')  # Nuevo tamaño en GB
        if not name or not new_size:
            return jsonify({'error': 'El nombre y el nuevo tamaño son obligatorios'}), 400

        # Reducir el tamaño de la partición
        command = f"sudo parted /dev/sda resizepart {name} {new_size}GB"
        subprocess.run(command, shell=True, check=True)

        return jsonify({'message': 'Partición reducida con éxito'}), 200
    except Exception as e:
        return jsonify({'error': f'Error al reducir la partición: {str(e)}'}), 500
def convert_to_gb(size_str):
    """
    Convierte un tamaño en formato humano (e.g., '50G', '1024M') a GB.
    """
    if size_str.endswith('G'):
        return float(size_str[:-1])
    elif size_str.endswith('M'):
        return float(size_str[:-1]) / 1024
    elif size_str.endswith('K'):
        return float(size_str[:-1]) / (1024 * 1024)
    else:
        return 0.0