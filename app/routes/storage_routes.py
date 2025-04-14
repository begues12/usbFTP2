from flask import Blueprint, request, jsonify, render_template
from app.models.connection_model import Connection
from app.routes.ftp_routes import ftp_bp
from app.routes.dropbox_routes import dropbox_bp
from app.routes.google_drive_routes import google_drive_bp
from app.storage.ftp_storage import FTPStorage
from app.storage.dropbox_storage import DropboxStorage
from app.storage.google_drive_storage import GoogleDriveStorage

storages = {
    'ftp': FTPStorage(),
    'dropbox': DropboxStorage(),
    'google_drive': GoogleDriveStorage()
}

storage_bp = Blueprint('storage', __name__)

# Registrar los Blueprints específicos
storage_bp.register_blueprint(ftp_bp, url_prefix='/ftp')
storage_bp.register_blueprint(dropbox_bp, url_prefix='/dropbox')
storage_bp.register_blueprint(google_drive_bp, url_prefix='/google_drive')

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
            if storage_instance:
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