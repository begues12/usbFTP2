from flask import Blueprint, request, jsonify, render_template
from app.models.connection_model import Connection
from app.storage.ftp_storage import FTPStorage
from app.storage.dropbox_storage import DropboxStorage
from app.storage.google_drive_storage import GoogleDriveStorage
from app.storage.local_storage import LocalStorage
from app.extensions import socketio, db  # Importar socketio y db desde extensions.py
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import os


storage_bp = Blueprint('storage', __name__)

storages = {
    'local'         : LocalStorage,
    'ftp'           : FTPStorage,
    'dropbox'       : DropboxStorage,
    'google_drive'  : GoogleDriveStorage
}

# -------------------------------
# Funciones de utilidad
# -------------------------------
def get_storage(connection_id):
    """
    Obtiene una instancia de Storage configurada dinámicamente
    según la conexión proporcionada.
    """
    connection = Connection.query.get(connection_id)
    if not connection:
        raise ValueError("Conexión no encontrada.")
        
    if connection.type == 'local':
        return LocalStorage(connection_id)
    elif connection.type == 'ftp':
        return FTPStorage(connection_id)
    elif connection.type == 'dropbox':
        return DropboxStorage(connection_id)
    elif connection.type == 'google_drive':
        return GoogleDriveStorage(connection_id)
    else:
        return ValueError("Tipo de conexión no soportado.")


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
            storage_instance = get_storage(connection.id)
            storage_instance.connect()  
            try:
                status = storage_instance.test_connection()
            except Exception as e:
                status = f"Error: {str(e)}"
                
            result.append({
                'id'            : storage_instance.id,
                'name'          : storage_instance.name,
                'type'          : storage_instance.type,
                'status'        : status,
                'has_password'  : storage_instance.has_password(),
            })

        return jsonify(result)

    # Renderizar el template para solicitudes normales
    return render_template('list_connections.html', connections=connections)

@storage_bp.route('/add_connection', methods=['POST'])
def add_connection():
    """
    Maneja la creación de una nueva conexión según el tipo de almacenamiento.
    """
    data = request.get_json() if request.is_json else request.form.to_dict()

    connection_name = data.get('name')
    connection_type = data.get('storage_type')
    credentials = data.copy()
    credentials.pop('name', None)  # Eliminar el nombre de las credenciales
    credentials.pop('type', None)  # Eliminar el tipo de las credenciales

    # Validar los datos básicos
    if not connection_name or not connection_type:
        return jsonify({'error': 'El nombre y el tipo de conexión son obligatorios.'}), 400

    # Validar el tipo de almacenamiento
    if connection_type not in storages:
        return jsonify({'error': f'Tipo de almacenamiento "{connection_type}" no soportado.'}), 400

    # Configuración específica para cada tipo de almacenamiento
    try:
        if connection_type == 'local':
            base_storage_path = "/home/usbFTP/"
            base_path = os.path.join(base_storage_path, connection_name)
            os.makedirs(base_path, exist_ok=True)
            credentials['base_path'] = base_path

        elif connection_type == 'ftp':
            required_keys = ['host', 'username', 'password']
            for key in required_keys:
                if key not in credentials:
                    return jsonify({'error': f'La credencial "{key}" es obligatoria para FTP.'}), 400

            ftp_storage = FTPStorage()
            ftp_storage.connect(credentials)

        elif connection_type == 'dropbox':
            if 'access_token' not in credentials:
                return jsonify({'error': 'El "access_token" es obligatorio para Dropbox.'}), 400

            dropbox_storage = DropboxStorage()
            dropbox_storage.connect(credentials)

        elif connection_type == 'google_drive':
            if 'credentials_file' not in credentials:
                return jsonify({'error': 'El archivo "credentials_file" es obligatorio para Google Drive.'}), 400

            google_drive_storage = GoogleDriveStorage()
            google_drive_storage.connect(credentials)

        else:
            return jsonify({'error': f'Tipo de almacenamiento "{connection_type}" no soportado.'}), 400

        connection = Connection()
        connection.set_new(
            name        = connection_name,
            type        = connection_type,
            credentials = credentials,
            password    = None
        )
    
        connection.save()

        return jsonify({'message': 'Conexión añadida con éxito.'}), 200

    except Exception as e:
        return jsonify({'error': f'Error al crear la conexión: {str(e)}'}), 500
            
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
def mount_connection(connection_id):
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
    Si el token ya existe y no ha expirado, lo reutiliza.
    """
    data = request.get_json()
    connection_id = data.get('connection_id')
    password = data.get('password')

    connection = get_storage(connection_id)
    if not connection:
        return jsonify({'error': 'Conexión no encontrada.'}), 404

    # Verificar si la contraseña es correcta
    if connection.check_password(password):
        token = connection.generate_token()
        return jsonify({
            'message': 'Contraseña correcta. Nuevo token generado.',
            'token': token,
            'type': connection.type,
            'folder_url': f"/storage/list/{connection_id}"
        }), 200
    else:
        return jsonify({'error': 'Contraseña incorrecta.'}), 403
         
@storage_bp.route('/set_password/<int:connection_id>', methods=['POST'])
def set_password(connection_id):
    """
    Configura o actualiza la contraseña de una conexión, almacenándola como un hash.
    """
    data        = request.get_json()
    password    = data.get('password')

    if not password:
        return jsonify({'error': 'La contraseña es obligatoria.'}), 400

    connection = get_storage(connection_id)

    if not connection:
        return jsonify({'error': 'Conexión no encontrada.'}), 404

    try:
        # Usar el método set_password del modelo para guardar la contraseña como hash
        connection.set_password(password)
        connection.save()
        return jsonify({'message': 'Contraseña configurada con éxito.'}), 200
    except Exception as e:
        return jsonify({'error': f'Error al configurar la contraseña: {str(e)}'}), 500
  
@storage_bp.route('/list/<int:connection_id>', methods=['POST'])
def list_connection_files(connection_id):
    """
    Lista los archivos y carpetas en la conexión especificada.
    """
    folder_path = request.args.get('folder_path', "")
    token       = request.headers.get('Authorization')

    try:
        storage = get_storage(connection_id)

        print(f"Validated: {storage.validate_token(token)}, Token: {token}")
        
        if token and storage.validate_token(token):
            file_list = storage.list_files(folder_path)
            return render_template(
                'storage_explorer.html',
                files=file_list,
                folder_path=folder_path,
                connection_id=connection_id,
                storage_type=storage.name
            )

        # Si no hay un token válido, verificar si se requiere contraseña
        if storage.has_password():
            return jsonify({'requires_password': True}), 403

        # Si no se requiere contraseña, listar los archivos
        file_list = storage.list_files(folder_path)
        return render_template(
            'storage_explorer.html',
            files=file_list,
            folder_path=folder_path,
            connection_id=connection_id,
            storage_type=storage.name
        )
    except Exception as e:
        return render_template(
            'storage_explorer.html',
            error=str(e),
            files=[],
            folder_path=folder_path,
            connection_id=connection_id,
            name="-"
        )
                
@storage_bp.route('/download_file/<int:connection_id>', methods=['GET'])
def download_file(connection_id):
    """
    Descarga un archivo desde la conexión especificada.
    """
    file_path = request.args.get('file_path')

    if not file_path:
        return jsonify({'error': 'La ruta del archivo es obligatoria.'}), 400

    try:
        storage = get_storage(connection_id)
        file_full_path = storage.download_file(file_path)

        # Enviar el archivo como respuesta
        return send_file(file_full_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': f'Error al descargar el archivo: {str(e)}'}), 500
    

@storage_bp.route('/delete_file/<int:connection_id>', methods=['POST'])
def delete_file(connection_id):
    """
    Elimina un archivo o carpeta en la conexión especificada.
    """
    data = request.form
    file_path = data.get('file_path')

    if not file_path:
        return jsonify({'error': 'La ruta del archivo es obligatoria.'}), 400

    try:
        storage = get_storage(connection_id)
        storage.delete_file(file_path)
        return jsonify({'message': 'Archivo eliminado con éxito.'}), 200
    except Exception as e:
        return jsonify({'error': f'Error al eliminar el archivo: {str(e)}'}), 500
