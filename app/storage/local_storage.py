import os

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
            
    def mount_to_gadget(self, mount_path):
        """
        Monta la carpeta local en el gadget utilizando fstab.
        """
        if not self.base_path:
            raise ValueError("Debe conectarse primero utilizando el método 'connect'.")

        # Asegurarse de que el directorio de montaje existe
        if not os.path.exists(mount_path):
            os.makedirs(mount_path)

        # Agregar entrada a fstab si no existe
        fstab_entry = f"{self.base_path} {mount_path} none bind 0 0\n"
        with open('/etc/fstab', 'r') as fstab:
            if fstab_entry not in fstab.read():
                with open('/etc/fstab', 'a') as fstab_append:
                    fstab_append.write(fstab_entry)

        # Montar la carpeta inmediatamente
        subprocess.run(['mount', mount_path], check=True)