from flask import Blueprint, request, jsonify, current_app, redirect, url_for, render_template
from app.models.connection_model import Connection  # Asegúrate de tener este modelo configurado
from app.storage.ftp_storage import FTPStorage
from app.storage.dropbox_storage import DropboxStorage
from app.storage.google_drive_storage import GoogleDriveStorage
import os

storage_bp = Blueprint('storage', __name__)

# Instancias de almacenamiento
storages = {
    'ftp': FTPStorage(),
    'dropbox': DropboxStorage(),
    'google_drive': GoogleDriveStorage()
}


@storage_bp.route('/list_usb', methods=['GET'])
def list_usb():
    """
    Lista los archivos en la carpeta USB.
    """
    usb_folder = current_app.config['USB_FOLDER']
    try:
        files = os.listdir(usb_folder)
        return jsonify({'files': files}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@storage_bp.route('/add_connection/<storage_type>', methods=['GET', 'POST'])
def add_connection(storage_type):
    """
    Maneja la creación de una nueva conexión según el tipo de almacenamiento.
    """
    if request.method == 'POST':
        # Obtener los datos del formulario
        connection_name = request.form.get('name')
        credentials = request.form.to_dict()

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
        return redirect(url_for('storage.list_connections'))

    # Renderizar el formulario para añadir una nueva conexión
    return render_template('add_connection.html', storage_type=storage_type)

@storage_bp.route('/connections', methods=['GET'])
def list_connections():
    """
    Lista todas las conexiones guardadas.
    """
    connections = Connection.get_all()
    return render_template('list_connections.html', connections=connections)


@storage_bp.route('/ftp/<int:connection_id>/list', methods=['GET'])
def list_ftp_files(connection_id):
    """
    Lista los archivos y carpetas de un servidor FTP guardado.
    """
    connection = Connection.get_by_id(connection_id)
    if not connection or connection.type != 'ftp':
        return jsonify({'error': 'Conexión FTP no encontrada'}), 404

    # Conectar al servidor FTP y listar archivos
    ftp_storage = FTPStorage()
    try:
        ftp_storage.connect(connection.credentials)
        files = ftp_storage.list_files()
        return render_template('ftp_explorer.html', files=files, connection=connection)
    except Exception as e:
        return jsonify({'error': str(e)}), 500