import subprocess
from flask import Blueprint, jsonify, request

storage_bp = Blueprint('storage', __name__)

@storage_bp.route('/get_storage_info', methods=['GET'])
def get_storage_info():
    try:
        # Ejecutar el comando 'df' para obtener información de las particiones
        result = subprocess.run(['df', '-h'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout

        # Procesar la salida del comando 'df'
        partitions = []
        total_storage = 0
        used_storage = 0
        system_storage = 0

        for line in output.splitlines()[1:]:  # Saltar la primera línea (encabezados)
            parts = line.split()
            if len(parts) < 6:
                continue

            # Extraer información relevante
            filesystem = parts[0]
            size = parts[1]
            used = parts[2]
            available = parts[3]
            mountpoint = parts[5]

            # Convertir tamaños a GB (si es necesario)
            size_gb = convert_to_gb(size)
            used_gb = convert_to_gb(used)

            # Sumar al almacenamiento total y usado
            total_storage += size_gb
            used_storage += used_gb

            # Clasificar el espacio del sistema
            if mountpoint in ['/', '/boot', '/home']:
                system_storage += size_gb
            else:
                # Agregar partición a la lista
                partitions.append({
                    'name': mountpoint,
                    'size': size_gb,
                    'type': filesystem
                })

        # Calcular el espacio no asignado
        unallocated_storage = total_storage - used_storage

        # Devolver los datos como JSON
        return jsonify({
            'partitions': partitions,
            'total_storage': round(total_storage, 2),
            'system_storage': round(system_storage, 2),
            'unallocated_storage': round(unallocated_storage, 2)
        })

    except Exception as e:
        return jsonify({'error': f'Error al obtener información del almacenamiento: {str(e)}'}), 500


@storage_bp.route('/create_partition', methods=['POST'])
def create_partition():
    try:
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


@storage_bp.route('/edit_partition', methods=['POST'])
def edit_partition():
    try:
        name = request.json.get('name')  # Nombre de la partición
        new_name = request.json.get('new_name')  # Nuevo nombre
        size = request.json.get('size')  # Nuevo tamaño
        if not name or not new_name or not size:
            return jsonify({'error': 'El nombre, el nuevo nombre y el tamaño son obligatorios'}), 400

        # Editar la partición (esto puede variar según el sistema)
        command = f"sudo parted /dev/sda resizepart {name} {size}GB"
        subprocess.run(command, shell=True, check=True)

        return jsonify({'message': 'Partición editada con éxito'}), 200
    except Exception as e:
        return jsonify({'error': f'Error al editar la partición: {str(e)}'}), 500


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