from flask import Blueprint, request, jsonify, redirect, url_for, render_template
from app.models.connection_model import Connection
from app.storage.ftp_storage import FTPStorage
from app.storage.dropbox_storage import DropboxStorage
from app.storage.google_drive_storage import GoogleDriveStorage

storage_bp = Blueprint('storage', __name__)

# Instancias de almacenamiento
storages = {
    'ftp': FTPStorage(),
    'dropbox': DropboxStorage(),
    'google_drive': GoogleDriveStorage()
}

# -------------------------------
# Rutas para gestionar conexiones
# -------------------------------

@storage_bp.route('/connections', methods=['GET'])
def list_connections():
    """
    Lista todas las conexiones guardadas.
    """
    connections = Connection.get_all()
    return render_template('list_connections.html', connections=connections)


@storage_bp.route('/add_connection/<storage_type>', methods=['POST'])
def add_connection(storage_type):
    """
    Maneja la creación de una nueva conexión según el tipo de almacenamiento.
    """
    if request.method == 'POST':
        # Obtener los datos del formulario o JSON
        if request.is_json:
            credentials = request.get_json()
        else:
            credentials = request.form.to_dict()

        connection_name = credentials.get('name')

        # Validar el tipo de almacenamiento
        if storage_type not in storages:
            return jsonify({'error': f'Tipo de almacenamiento "{storage_type}" no soportado'}), 400

        # Validar las credenciales antes de guardar
        storage_instance = storages[storage_type]
        try:
            storage_instance.connect(credentials)  # Intenta conectar con las credenciales
        except Exception as e:
            return jsonify({'error': f'Error al validar la conexión: {str(e)}'}), 400

        # Guardar la conexión en la base de datos
        connection = Connection(name=connection_name, type=storage_type, credentials=credentials)
        connection.save()
        return jsonify({'message': 'Conexión añadida con éxito'}), 200
# -------------------------------
# Rutas para FTP
# -------------------------------

@storage_bp.route('/ftp/<int:connection_id>/list', methods=['GET'])
def list_ftp_files(connection_id):
    """
    Lista los archivos y carpetas de un servidor FTP guardado.
    """
    connection = Connection.get_by_id(connection_id)
    if not connection or connection.type != 'ftp':
        return jsonify({'error': 'Conexión FTP no encontrada'}), 404

    ftp_storage = FTPStorage()
    try:
        ftp_storage.connect(connection.credentials)
        files = ftp_storage.list_files()
        ftp_storage.disconnect()
        return render_template('ftp_explorer.html', files=files, connection=connection)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# -------------------------------
# Rutas para Dropbox
# -------------------------------

@storage_bp.route('/dropbox/<int:connection_id>/list', methods=['GET'])
def list_dropbox_files(connection_id):
    """
    Lista los archivos y carpetas de una conexión de Dropbox guardada.
    """
    connection = Connection.get_by_id(connection_id)
    if not connection or connection.type != 'dropbox':
        return jsonify({'error': 'Conexión Dropbox no encontrada'}), 404

    dropbox_storage = DropboxStorage()
    try:
        dropbox_storage.login(connection.credentials)
        # Implementar lógica para listar archivos en Dropbox
        files = dropbox_storage.list_files()  # Debes implementar este método en DropboxStorage
        dropbox_storage.logout()
        return render_template('dropbox_explorer.html', files=files, connection=connection)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# -------------------------------
# Rutas para Google Drive
# -------------------------------

@storage_bp.route('/google_drive/<int:connection_id>/list', methods=['GET'])
def list_google_drive_files(connection_id):
    """
    Lista los archivos y carpetas de una conexión de Google Drive guardada.
    """
    connection = Connection.get_by_id(connection_id)
    if not connection or connection.type != 'google_drive':
        return jsonify({'error': 'Conexión Google Drive no encontrada'}), 404

    google_drive_storage = GoogleDriveStorage()
    try:
        google_drive_storage.login(connection.credentials)
        # Implementar lógica para listar archivos en Google Drive
        files = google_drive_storage.list_files()  # Debes implementar este método en GoogleDriveStorage
        google_drive_storage.logout()
        return render_template('google_drive_explorer.html', files=files, connection=connection)
    except Exception as e:
        return jsonify({'error': str(e)}), 500