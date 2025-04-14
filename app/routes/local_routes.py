from flask import Blueprint, jsonify, request, send_file, render_template
from app.storage.local_storage import LocalStorage
import os
from app import db
from app.models.connection_model import Connection

local_bp = Blueprint('local', __name__)

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

@local_bp.route('/<int:connection_id>/list', methods=['GET'])
def list_local_files(connection_id):
    """
    Lista los archivos y carpetas en el almacenamiento local y renderiza la plantilla.
    """
    folder_path = request.args.get('folder_path', "")
    try:
        # Obtener la instancia de LocalStorage
        local_storage = get_local_storage(connection_id)
        files = local_storage.list_files(folder_path)

        # Renderizar la plantilla con los archivos y carpetas
        return render_template(
            'files_explorer/local_explorer.html',
            files=files,
            connection_id=connection_id,
            folder_path=folder_path
        )
    except Exception as e:
        # Renderizar un mensaje de error en caso de fallo
        return render_template(
            'files_explorer/local_explorer.html',
            files=[],
            connection_id=connection_id,
            folder_path=folder_path,
            error=str(e)
        )
        
@local_bp.route('/<int:connection_id>/download', methods=['GET'])
def download_local_file(connection_id):
    """
    Descarga un archivo del almacenamiento local.
    """
    file_path = request.args.get('file_path')
    try:
        local_storage = get_local_storage(connection_id)
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
        local_storage = get_local_storage(connection_id)
        local_storage.delete_file(file_path)
        return jsonify({'message': 'Archivo eliminado con éxito'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
        
@local_bp.route('/prepare', methods=['POST'])
def prepare_local_folders():
    """
    Prepara las carpetas locales y backing files para todas las conexiones locales.
    """
    connections = Connection.query.filter_by(type='local').all()
    for connection in connections:
        try:
            local_storage = get_local_storage(connection.id)
            backing_file = f"/home/usbFTP/backing_{connection.id}.img"
            local_storage.prepare_backing_file(backing_file)
            local_storage.sync_folder_to_backing_file(backing_file)
        except Exception as e:
            print(f"Error al preparar la conexión {connection.id}: {e}")
    return jsonify({'message': 'Preparación completada'}), 200