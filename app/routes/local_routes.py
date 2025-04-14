from flask import Blueprint, jsonify, request, send_file, render_template
from app.storage.local_storage import LocalStorage

local_bp = Blueprint('local', __name__)
local_storage = LocalStorage(base_path="c:/Users/afuentes/Documents/usbFTP2/local_storage")  # Cambia la ruta según sea necesario

@local_bp.route('/add_connection/local', methods=['POST'])
def add_local_connection():
    """
    Crea una nueva conexión de tipo LocalStorage.
    """
    if request.method == 'POST':
        # Obtener los datos del formulario o JSON
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        connection_name = data.get('name')
        base_path = data.get('base_path')

        if not connection_name or not base_path:
            return jsonify({'error': 'El nombre y la ruta base son obligatorios'}), 400

        # Validar que la ruta base exista o crearla
        try:
            os.makedirs(base_path, exist_ok=True)
        except Exception as e:
            return jsonify({'error': f'Error al crear la ruta base: {str(e)}'}), 500

        # Guardar la conexión en la base de datos
        connection = Connection(name=connection_name, type='local', credentials={'base_path': base_path})
        connection.save()

        return jsonify({'message': 'Conexión LocalStorage añadida con éxito'}), 200

@local_bp.route('/<int:connection_id>/list', methods=['GET'])
def list_local_files(connection_id):
    """
    Lista los archivos y carpetas en el almacenamiento local.
    """
    folder_path = request.args.get('folder_path', "")
    try:
        files = local_storage.list_files(folder_path)
        return render_template('local_explorer.html', files=files, connection_id=connection_id)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@local_bp.route('/<int:connection_id>/download', methods=['GET'])
def download_local_file(connection_id):
    """
    Descarga un archivo del almacenamiento local.
    """
    file_path = request.args.get('file_path')
    try:
        full_path = local_storage.download_file(file_path)
        return send_file(full_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@local_bp.route('/<int:connection_id>/delete', methods=['POST'])
def delete_local_file(connection_id):
    """
    Elimina un archivo o carpeta del almacenamiento local.
    """
    file_path = request.form.get('file_path')
    try:
        local_storage.delete_file(file_path)
        return jsonify({'message': 'Archivo eliminado con éxito'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500