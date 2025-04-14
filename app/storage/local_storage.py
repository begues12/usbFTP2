import os
import subprocess


class LocalStorage:
    def __init__(self, base_path=None):
        """
        Inicializa el almacenamiento local con una carpeta base.
        """
        self.base_path = base_path

    def connect(self, credentials):
        """
        Configura la ruta base a partir de las credenciales proporcionadas.
        """
        self.base_path = credentials.get('base_path')
        if not self.base_path:
            raise ValueError("Las credenciales deben incluir 'base_path'.")
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

    def disconnect(self, credentials):
        """
        Realiza las operaciones necesarias para desconectar LocalStorage.
        """
        base_path = credentials.get('base_path')
        if base_path and os.path.exists(base_path):
            # Aquí puedes realizar operaciones adicionales si es necesario
            print(f"Desmontando LocalStorage en {base_path}")
        
    def list_files(self, folder_path=""):
        """
        Lista los archivos y carpetas en la ruta especificada.
        """
        if not self.base_path:
            raise ValueError("Debe conectarse primero utilizando el método 'connect'.")

        full_path = os.path.join(self.base_path, folder_path)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"La carpeta {full_path} no existe.")

        files = []
        for item in os.listdir(full_path):
            item_path = os.path.join(full_path, item)
            files.append({
                "name": item,
                "is_dir": os.path.isdir(item_path),
                "size": os.path.getsize(item_path) if os.path.isfile(item_path) else None,
                "modified_time": os.path.getmtime(item_path),
                "path": os.path.relpath(item_path, self.base_path)
            })
        return files

    def download_file(self, file_path):
        """
        Devuelve la ruta completa del archivo para su descarga.
        """
        if not self.base_path:
            raise ValueError("Debe conectarse primero utilizando el método 'connect'.")

        full_path = os.path.join(self.base_path, file_path)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"El archivo {file_path} no existe.")
        return full_path

    def delete_file(self, file_path):
        """
        Elimina un archivo o carpeta.
        """
        if not self.base_path:
            raise ValueError("Debe conectarse primero utilizando el método 'connect'.")

        full_path = os.path.join(self.base_path, file_path)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"El archivo o carpeta {file_path} no existe.")
        if os.path.isdir(full_path):
            os.rmdir(full_path)
        else:
            os.remove(full_path)

    def create_folder(self, folder_name):
        """
        Crea una nueva carpeta en la ruta base.
        """
        if not self.base_path:
            raise ValueError("Debe conectarse primero utilizando el método 'connect'.")

        full_path = os.path.join(self.base_path, folder_name)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
            
    def mount_to_gadget(self, mount_path, backing_file, lun_config_path):
        """
        Monta la carpeta local como un dispositivo USB utilizando gadget mode.
        """
        # Paso 1: Verificar si ya está montado
        if os.path.ismount(mount_path):
            print(f"{mount_path} ya está montado. Procediendo a desmontarlo...")
            subprocess.run(['sudo', 'umount', mount_path], check=True)

        # Paso 2: Crear backing file si no existe
        if not os.path.exists(backing_file):
            print(f"Creando backing file {backing_file}...")
            subprocess.run(['sudo', 'dd', 'if=/dev/zero', f'of={backing_file}', 'bs=1M', 'count=64'], check=True)
            print(f"Formateando {backing_file} como FAT32...")
            subprocess.run(['sudo', 'mkfs.vfat', backing_file], check=True)

        # Paso 3: Sincronizar contenido de la carpeta con el backing file
        temp_mount = "/mnt/temp_backing"
        os.makedirs(temp_mount, exist_ok=True)
        try:
            print(f"Montando {backing_file} temporalmente en {temp_mount}...")
            subprocess.run(['sudo', 'mount', '-o', 'loop', backing_file, temp_mount], check=True)
            print(f"Sincronizando contenido de {self.base_path} con {backing_file}...")
            subprocess.run(['sudo', 'rsync', '-av', f"{self.base_path}/", temp_mount], check=True)
        finally:
            print(f"Desmontando {temp_mount}...")
            subprocess.run(['sudo', 'umount', temp_mount], check=True)
            os.rmdir(temp_mount)

        # Paso 4: Actualizar configuración del gadget USB
        print(f"Actualizando configuración del gadget USB en {lun_config_path}...")
        with open(lun_config_path, "w") as lun_file:
            lun_file.write(backing_file)

        print("Operación completada con éxito.")