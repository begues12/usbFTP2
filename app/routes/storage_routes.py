from flask import Blueprint, request, jsonify, render_template
from app.models.connection_model import Connection
from app.models.token_model import Token
from app.routes.ftp_routes import ftp_bp
from app.routes.dropbox_routes import dropbox_bp
from app.routes.google_drive_routes import google_drive_bp
from app.storage.ftp_storage import FTPStorage
from app.storage.dropbox_storage import DropboxStorage
from app.storage.google_drive_storage import GoogleDriveStorage
from app.storage.local_storage import LocalStorage
from app.routes.local_routes import local_bp
from app.extensions import socketio, db  # Importar socketio y db desde extensions.py
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
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
                'status': status,  # Estado de la conexión
                'has_password': bool(connection.has_password),  # Verificar si tiene contraseña
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
    
@storage_bp.route('/submit_password', methods=['POST'])
def submit_password():
    """
    Valida la contraseña enviada por el cliente y genera un token temporal.
    """
    data = request.get_json()
    connection_id = data.get('connection_id')
    password = data.get('password')

    connection = Connection.query.get(connection_id)
    if not connection:
        return jsonify({'error': 'Conexión no encontrada.'}), 404

    if connection.check_password(password):
        # Generar un token temporal
        token = Token.generate_token(connection_id)

        # Devolver el token y el tipo de conexión
        return jsonify({
            'message': 'Contraseña correcta.',
            'token': token,
            'type': connection.type,
            'folder_url': f"/storage/access_folder/{connection_id}"
        }), 200
    else:
        return jsonify({'error': 'Contraseña incorrecta.'}), 403
     
@storage_bp.route('/set_password/<int:connection_id>', methods=['POST'])
def set_password(connection_id):
    """
    Configura o actualiza la contraseña de una conexión, almacenándola como un hash.
    """
    data = request.get_json()
    password = data.get('password')

    if not password:
        return jsonify({'error': 'La contraseña es obligatoria.'}), 400

    connection = Connection.query.get(connection_id)

    if not connection:
        return jsonify({'error': 'Conexión no encontrada.'}), 404

    try:
        # Usar el método set_password del modelo para guardar la contraseña como hash
        connection.set_password(password)
        connection.save()
        return jsonify({'message': 'Contraseña configurada con éxito.'}), 200
    except Exception as e:
        return jsonify({'error': f'Error al configurar la contraseña: {str(e)}'}), 500

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

@storage_bp.route('/access_connection/<int:connection_id>', methods=['GET'])
def access_folder(connection_id):
    """
    Valida el token o la contraseña y devuelve el tipo de conexión para que el frontend construya la ruta.
    """
    folder_path = request.args.get('folder_path', "")
    token = request.headers.get('Authorization')  # Leer el token del encabezado

    try:
        # Obtener la conexión
        connection = Connection.query.get(connection_id)
        if not connection:
            return jsonify({'error': 'Conexión no encontrada.'}), 404

        # Verificar si la conexión tiene una contraseña configurada
        if connection.has_password:
            if not token:
                return jsonify({'requires_password': True}), 403
            if not Token.validate_token(token):  # Validar el token
                return jsonify({'error': 'Token inválido o expirado.', 'requires_password': True}), 403

        # Devolver el tipo de conexión y la carpeta
        return jsonify({
            'type': connection.type,
            'folder_path': folder_path
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@storage_bp.route('/list/<int:connection_id>', methods=['GET'])
def list_connection_files(connection_id):
    """
    Lista los archivos y carpetas en la conexión especificada.
    """
    #Get in post the folder path
    folder_path = request.args.get('folder_path', "")
    token = request.headers.get('Authorization')
 
    try:
        connection = Connection.query.get(connection_id)
        if not connection:
            return jsonify({'error': 'Conexión no encontrada.'}), 404

        if connection.has_password:
            if not token:
                return jsonify({'requires_password': True}), 403
            if not Token.validate_token(token):  # Validar el token
                return jsonify({'error': 'Token inválido o expirado.', 'requires_password': True}), 403

        
        storage_instance = storages.get(connection.type)
        if not storage_instance:
            return jsonify({'error': f'Tipo de conexión "{connection.type}" no soportado'}), 400 

        storage = storage_instance.list_files(folder_path)
        
        return jsonify(storage), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500