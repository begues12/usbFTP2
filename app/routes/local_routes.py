from flask import Blueprint, jsonify, request, send_file, render_template
from app.storage.local_storage import LocalStorage
import os
from app import db
from app.models.connection_model import Connection

local_bp = Blueprint('local', __name__)

def get_local_storage(connection_id):
    """
    Obtiene una instancia de LocalStorage configurada dinámicamente
    según la conexión proporcionada.
    """
    connection = Connection.query.get(connection_id)
    if not connection:
        raise ValueError("Conexión no encontrada.")
    if connection.type != 'local':
        raise ValueError("El tipo de conexión no es 'local'.")
    credentials = connection.credentials
    base_path = credentials.get('base_path')
    if not base_path:
        raise ValueError("La conexión no tiene un 'base_path' configurado.")
    return LocalStorage(base_path=base_path)

@local_bp.route('/<int:connection_id>/list', methods=['GET'])
def list_local_files(connection_id):
    """
    Lista los archivos y carpetas en el almacenamiento local y verifica si requiere un token válido.
    """
    folder_path = request.args.get('folder_path', "")
    token = request.headers.get('Authorization')  # Leer el token del encabezado

    try:
        # Validar el token
        if not Token.validate_token(token):
            return jsonify({'error': 'Token inválido o expirado.'}), 403

        # Obtener la instancia de LocalStorage
        local_storage = get_local_storage(connection_id)
        files = local_storage.list_files(folder_path)

        # Renderizar la plantilla con los archivos y carpetas
        return render_template(
            'files_explorer/local_explorer.html',
            files=files,
            connection_id=connection_id,
            folder_path=folder_path
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500
                        
@local_bp.route('/<int:connection_id>/download', methods=['GET'])
def download_local_file(connection_id):
    """
    Descarga un archivo del almacenamiento local.
    """
    file_path = request.args.get('file_path')
    try:
        local_storage = get_local_storage(connection_id)
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
        local_storage = get_local_storage(connection_id)
        local_storage.delete_file(file_path)
        return jsonify({'message': 'Archivo eliminado con éxito'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


        
@local_bp.route('/prepare', methods=['POST'])
def prepare_local_folders():
    """
    Prepara las carpetas locales y backing files para todas las conexiones locales.
    """
    connections = Connection.query.filter_by(type='local').all()
    for connection in connections:
        try:
            local_storage = get_local_storage(connection.id)
            backing_file = f"/home/usbFTP/backing_{connection.id}.img"
            local_storage.prepare_backing_file(backing_file)
            local_storage.sync_folder_to_backing_file(backing_file)
        except Exception as e:
            print(f"Error al preparar la conexión {connection.id}: {e}")
    return jsonify({'message': 'Preparación completada'}), 200