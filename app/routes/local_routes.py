from flask import Blueprint, jsonify, request, send_file, render_template
from app.storage.local_storage import LocalStorage
import os 
from app import db
from app.models.connection_model import Connection

local_bp = Blueprint('local', __name__)
local_storage = LocalStorage(base_path="c:/Users/afuentes/Documents/usbFTP2/local_storage")  # Cambia la ruta según sea necesario

@local_bp.route('/<int:connection_id>/list', methods=['GET'])
def list_local_files(connection_id):
    """
    Lista los archivos y carpetas en el almacenamiento local.
    """
    folder_path = request.args.get('folder_path', "")
    try:
        files = local_storage.list_files(folder_path)
        return render_template('local_explorer.html', files=files, connection_id=connection_id)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@local_bp.route('/<int:connection_id>/download', methods=['GET'])
def download_local_file(connection_id):
    """
    Descarga un archivo del almacenamiento local.
    """
    file_path = request.args.get('file_path')
    try:
        full_path = local_storage.download_file(file_path)
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
        local_storage.delete_file(file_path)
        return jsonify({'message': 'Archivo eliminado con éxito'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@local_bp.route('/<int:connection_id>/mount', methods=['POST'])
def mount_local_folder(connection_id):
    """
    Monta una carpeta local para que sea accesible a través del gadget.
    """
    try:
        connection = Connection.query.get(connection_id)
        if not connection:
            return jsonify({'error': 'Conexión no encontrada'}), 404

        mount_path = f"/mnt/gadget/{connection.name}"
        local_storage.connect(connection.credentials)
        local_storage.mount_to_gadget(mount_path)

        return jsonify({'message': f'Carpeta montada en {mount_path}'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500