from flask import Blueprint, jsonify, render_template
from app.models.connection_model import Connection
from app.storage.google_drive_storage import GoogleDriveStorage

google_drive_bp = Blueprint('google_drive', __name__)

@google_drive_bp.route('/<int:connection_id>/list', methods=['GET'])
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
        files = google_drive_storage.list_files()  # Implementar este método en GoogleDriveStorage
        google_drive_storage.logout()
        return render_template('google_drive_explorer.html', files=files, connection=connection)
    except Exception as e:
        return jsonify({'error': str(e)}), 500