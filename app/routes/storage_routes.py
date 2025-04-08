import subprocess
from flask import Blueprint, jsonify

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
            'unallocated_storage': round(unallocated_storage, 2)
        })

    except Exception as e:
        return jsonify({'error': f'Error al obtener información del almacenamiento: {str(e)}'}), 500


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