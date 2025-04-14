from flask import Blueprint, request, jsonify, render_template
from app.models.connection_model import Connection
from app.storage.ftp_storage import FTPStorage

ftp_bp = Blueprint('ftp', __name__)

@ftp_bp.route('/<int:connection_id>/list', methods=['GET'])
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
        files = []

        # Obtener la lista de archivos y carpetas
        for item in ftp_storage.ftp.mlsd():
            name, metadata = item
            files.append({
                "name": name,
                "is_dir": metadata["type"] == "dir",
                "size": metadata.get("size"),
                "modified_time": metadata.get("modify"),
                "path": f"/{name}"
            })

        ftp_storage.disconnect()
        return render_template('ftp_explorer.html', files=files, connection=connection)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ftp_bp.route('/<int:connection_id>/download', methods=['GET'])
def download_file(connection_id):
    """
    Descarga un archivo del servidor FTP.
    """
    file_path = request.args.get('file_path')
    if not file_path:
        return jsonify({"error": "No se proporcionó la ruta del archivo"}), 400

    try:
        connection = Connection.query.get(connection_id)
        if not connection or connection.type != 'ftp':
            return jsonify({'error': 'Conexión FTP no encontrada'}), 404

        ftp_storage = FTPStorage()
        ftp_storage.connect(connection.credentials)

        # Descargar el archivo como un flujo de bytes
        file_data = []
        ftp_storage.ftp.retrbinary(f"RETR {file_path}", file_data.append)
        ftp_storage.disconnect()

        # Unir los datos y enviarlos como respuesta
        response = make_response(b"".join(file_data))
        response.headers['Content-Disposition'] = f'attachment; filename="{file_path.split("/")[-1]}"'
        response.headers['Content-Type'] = 'application/octet-stream'
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ftp_bp.route('/<int:connection_id>/delete', methods=['POST'])
def delete_file(connection_id):
    """
    Elimina un archivo del servidor FTP.
    """
    file_path = request.form.get('file_path')
    if not file_path:
        return jsonify({"error": "No se proporcionó la ruta del archivo"}), 400

    try:
        connection = Connection.query.get(connection_id)
        if not connection or connection.type != 'ftp':
            return jsonify({'error': 'Conexión FTP no encontrada'}), 404

        ftp_storage = FTPStorage()
        ftp_storage.connect(connection.credentials)
        ftp_storage.ftp.delete(file_path)
        ftp_storage.disconnect()

        return jsonify({"message": "Archivo eliminado con éxito"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ftp_bp.route('/<int:connection_id>/view', methods=['GET'])
def view_file(connection_id):
    """
    Muestra el contenido de un archivo de texto plano.
    """
    file_path = request.args.get('file_path')
    if not file_path:
        return "Ruta del archivo no proporcionada", 400

    try:
        connection = Connection.query.get(connection_id)
        ftp_storage = FTPStorage()
        ftp_storage.connect(connection.credentials)

        # Descargar el contenido del archivo como texto
        content = []
        ftp_storage.ftp.retrlines(f"RETR {file_path}", content.append)
        return render_template('view_file.html', content="\n".join(content), file_name=file_path)
    except Exception as e:
        return f"Error al leer el archivo: {str(e)}", 500
    
@ftp_bp.route('/<int:connection_id>/explore', methods=['GET'])
def explore_folder(connection_id):
    """
    Explora el contenido de una carpeta en el servidor FTP.
    """
    folder_path = request.args.get('folder_path', '/')
    connection = Connection.query.get(connection_id)
    if not connection or connection.type != 'ftp':
        return jsonify({'error': 'Conexión FTP no encontrada'}), 404

    ftp_storage = FTPStorage()
    try:
        ftp_storage.connect(connection.credentials)
        files = []

        # Obtener la lista de archivos y carpetas en la carpeta especificada
        for item in ftp_storage.ftp.mlsd(folder_path):
            name, metadata = item
            files.append({
                "name": name,
                "is_dir": metadata["type"] == "dir",
                "size": metadata.get("size"),
                "modified_time": metadata.get("modify"),
                "path": f"{folder_path}/{name}"
            })

        ftp_storage.disconnect()
        return render_template('ftp_explorer.html', files=files, connection=connection)
    except Exception as e:
        return jsonify({'error': str(e)}), 500