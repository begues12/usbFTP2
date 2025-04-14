from flask import Blueprint, jsonify, render_template
from app.models.connection_model import Connection
from app.storage.dropbox_storage import DropboxStorage

dropbox_bp = Blueprint('dropbox', __name__)

@dropbox_bp.route('/<int:connection_id>/list', methods=['GET'])
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
        files = dropbox_storage.list_files()  # Implementar este método en DropboxStorage
        dropbox_storage.logout()
        return render_template('dropbox_explorer.html', files=files, connection=connection)
    except Exception as e:
        return jsonify({'error': str(e)}), 500