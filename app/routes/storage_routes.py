from flask import Blueprint, request, jsonify, render_template
from app.models.connection_model import Connection
from app.routes.ftp_routes import ftp_bp
from app.routes.dropbox_routes import dropbox_bp
from app.routes.google_drive_routes import google_drive_bp
from app.storage.ftp_storage import FTPStorage
from app.storage.dropbox_storage import DropboxStorage
from app.storage.google_drive_storage import GoogleDriveStorage
from app.storage.local_storage import LocalStorage
from app.routes.local_routes import local_bp
from app.extensions import socketio, db  # Importar socketio y db desde extensions.py
import os

storages = {
    'ftp'           : FTPStorage(),
    'dropbox'       : DropboxStorage(),
    'google_drive'  : GoogleDriveStorage(),
    'local'         : LocalStorage()     
}

storage_bp = Blueprint('storage', __name__)

# Registrar los Blueprints específicos
storage_bp.register_blueprint(ftp_bp, url_prefix='/ftp')
storage_bp.register_blueprint(dropbox_bp, url_prefix='/dropbox')
storage_bp.register_blueprint(google_drive_bp, url_prefix='/google_drive')
storage_bp.register_blueprint(local_bp, url_prefix='/local')

# -------------------------------
# Rutas generales
# -------------------------------

@storage_bp.route('/connections', methods=['GET'])
def list_connections():
    """
    Lista todas las conexiones guardadas y prueba rápidamente su estado.
    """
    connections = Connection.get_all()

    # Si la solicitud es AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        result = []
        for connection in connections:
            # Probar la conexión rápidamente
            storage_instance = storages.get(connection.type)
            status = 'pending'  # Estado predeterminado

            # Verificar si la conexión está montada
            if connection.type == 'local':
                mount_path = connection.credentials.get('base_path')
                status = 'mount' if os.path.exists(mount_path) else 'error'
            elif storage_instance:
                try:
                    storage_instance.test_connection(connection.credentials)
                    status = 'success'
                except Exception:
                    status = 'error'
            else:
                status = 'unsupported'

            result.append({
                'id': connection.id,
                'name': connection.name,
                'type': connection.type,
                'status': status  # Estado de la conexión
            })

        return jsonify(result)

    # Renderizar el template para solicitudes normales
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

        if storage_type == 'local':
            base_storage_path = "/home/usbFTP/"
            base_path = os.path.join(base_storage_path, connection_name)

            try:
                os.makedirs(base_path, exist_ok=True)
                credentials['base_path'] = base_path 
            except Exception as e:
                return jsonify({'error': f'Error al crear la carpeta local: {str(e)}'}), 500

        storage_instance = storages[storage_type]
        try:
            storage_instance.connect(credentials) 
        except Exception as e:
            return jsonify({'error': f'Error al validar la conexión: {str(e)}'}), 400

        connection = Connection(name=connection_name, type=storage_type, credentials=credentials)
        connection.save()
        return jsonify({'message': 'Conexión añadida con éxito'}), 200
        
@storage_bp.route('/delete_connection/<int:connection_id>', methods=['POST'])
def delete_connection(connection_id):
    """
    Elimina una conexión de cualquier tipo.
    """
    # Obtener la conexión de la base de datos
    connection = Connection.query.get(connection_id)
    if not connection:
        return jsonify({'error': 'Conexión no encontrada'}), 404

    # Determinar el tipo de conexión
    connection_type = connection.type
    storage_instance = storages.get(connection_type)

    if not storage_instance:
        return jsonify({'error': f'Tipo de conexión "{connection_type}" no soportado'}), 400

    try:
        # Llamar a una función abstracta para desmontar/desconectar
        if hasattr(storage_instance, 'disconnect'):
            storage_instance.disconnect(connection.credentials)

        # Eliminar la conexión de la base de datos
        db.session.delete(connection)
        db.session.commit()

        return jsonify({'message': 'Conexión eliminada con éxito'}), 200
    except Exception as e:
        return jsonify({'error': f'Error al eliminar la conexión: {str(e)}'}), 500
            
@storage_bp.route('/mount/<int:connection_id>', methods=['POST'])
def mount_folder(connection_id):
    """
    Monta una carpeta para que sea accesible con el gadget mode.
    """
    connection = Connection.query.get(connection_id)
    if not connection:
        return jsonify({'error': 'Conexión no encontrada'}), 404

    connection_type = connection.type
    storage_instance = storages.get(connection_type)

    if not storage_instance:
        return jsonify({'error': f'Tipo de conexión "{connection_type}" no soportado'}), 400

    try:
        mount_path = f"/mnt/gadget/{connection.name}"
        backing_file = f"/home/usbFTP/backing_{connection.id}.img"
        lun_config_path = f"/sys/kernel/config/usb_gadget/mygadget/functions/mass_storage.0/lun.0/file"

        storage_instance.mount_to_gadget(mount_path, backing_file, lun_config_path)
        return jsonify({'message': f'Carpeta montada en {mount_path} y expuesta como dispositivo USB.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@socketio.on('access_folder')
def handle_access_folder(data):
    """
    Maneja el evento de intento de acceso a una carpeta protegida.
    """
    connection_id = data.get('connection_id')
    connection = Connection.query.get(connection_id)

    if not connection:
        emit('access_denied', {'message': 'Conexión no encontrada'})
        return

    # Verificar si la carpeta está protegida con contraseña
    if 'password' in connection.credentials:
        emit('password_required', {'message': f'La carpeta "{connection.name}" está protegida con contraseña.'})
    else:
        emit('access_granted', {'message': f'Acceso concedido a la carpeta "{connection.name}".'})


@socketio.on('submit_password')
def handle_submit_password(data):
    """
    Maneja el envío de la contraseña por parte del cliente.
    """
    connection_id = data.get('connection_id')
    password = data.get('password')

    connection = Connection.query.get(connection_id)

    if not connection:
        emit('access_denied', {'message': 'Conexión no encontrada'})
        return

    # Validar la contraseña
    if connection.credentials.get('password') == password:
        emit('access_granted', {'message': f'Acceso concedido a la carpeta "{connection.name}".'})
    else:
        emit('access_denied', {'message': 'Contraseña incorrecta. Acceso denegado.'})