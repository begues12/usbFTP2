from flask import Blueprint, jsonify, request, send_file, render_template
from app.storage.local_storage import LocalStorage
from app.storage.ftp_storage import FTPStorage
from app.storage.dropbox_storage import DropboxStorage
from app.storage.google_drive_storage import GoogleDriveStorage
import os
from app import db
from app.models.connection_model import Connection
from app.models.token_model import Token


local_bp = Blueprint('local', __name__)

def get_storage(connection_id):
    """
    Obtiene una instancia de Storage configurada dinámicamente
    según la conexión proporcionada.
    """
    connection = Connection.query.get(connection_id)
    if not connection:
        raise ValueError("Conexión no encontrada.")
        
    if connection.type == 'local':
        return LocalStorage(connection.credentials)
    elif connection.type == 'ftp':
        return FTPStorage(connection.credentials)
    elif connection.type == 'dropbox':
        return DropboxStorage(connection.credentials)
    elif connection.type == 'google_drive':
        return GoogleDriveStorage(connection.credentials)
    else:
        return ValueError("Tipo de conexión no soportado.")

@local_bp.route('/<int:connection_id>/list', methods=['GET'])
def list_local_files(connection_id):
    """
    Lista los archivos y carpetas en el almacenamiento local y verifica si requiere un token válido.
    Si la conexión tiene una contraseña configurada, valida el token.
    Si no tiene contraseña configurada, muestra directamente el explorador de archivos.
    """
    folder_path = request.args.get('folder_path', "")
    token       = request.headers.get('Authorization')  # Leer el token del encabezado

    try:
        connection = Connection.query.get(connection_id)
        
        if not connection:
            return jsonify({'error': 'Conexión no encontrada.'}), 404

        if connection.has_password():
            if not token:
                return jsonify({'requires_password': True}), 403
            if not Token.validate_token(token):  # Validar el token
                return jsonify({'error': 'Token inválido o expirado.', 'requires_password': True}), 403

        storage = get_storage(connection_id)
        files   = storage.list_files(folder_path)

        return ({
            'root_path'         : storage.base_path,
            'files'             : files,
            'requires_password' : connection.has_password()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
                                            
@local_bp.route('/<int:connection_id>/download', methods=['GET'])
def download_local_file(connection_id):
    """
    Descarga un archivo del almacenamiento local.
    """
    file_path = request.args.get('file_path')
    try:
        local_storage   = get_storage(connection_id)
        full_path       = local_storage.download_file(file_path)
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