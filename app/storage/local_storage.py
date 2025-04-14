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
            
    def prepare_backing_file(self, backing_file):
        """
        Crea el backing file si no existe y lo formatea.
        """
        if not os.path.exists(backing_file):
            print(f"Creando backing file {backing_file}...")
            subprocess.run(['sudo', 'dd', 'if=/dev/zero', f'of={backing_file}', 'bs=1M', 'count=64'], check=True)
            print(f"Formateando {backing_file} como FAT32...")
            subprocess.run(['sudo', 'mkfs.vfat', backing_file], check=True)

    def sync_folder_to_backing_file(self, backing_file):
        """
        Sincroniza el contenido de la carpeta con el backing file.
        """
        if not self.base_path:
            raise ValueError("Debe conectarse primero utilizando el método 'connect'.")

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

    def configure_gadget(self):
        """
        Configura automáticamente el gadget USB.
        """
        gadget_path = "/sys/kernel/config/usb_gadget/mygadget"
        if not os.path.exists(gadget_path):
            print("Configurando el gadget USB...")
            subprocess.run(['sudo', 'mkdir', '-p', gadget_path], check=True)
            subprocess.run(['sudo', 'sh', '-c', f'echo 0x1d6b > {gadget_path}/idVendor'], check=True)
            subprocess.run(['sudo', 'sh', '-c', f'echo 0x0104 > {gadget_path}/idProduct'], check=True)
            subprocess.run(['sudo', 'sh', '-c', f'echo 0x0100 > {gadget_path}/bcdDevice'], check=True)
            subprocess.run(['sudo', 'sh', '-c', f'echo 0x0200 > {gadget_path}/bcdUSB'], check=True)

            os.makedirs(f"{gadget_path}/strings/0x409", exist_ok=True)
            subprocess.run(['sudo', 'sh', '-c', f'echo "0123456789" > {gadget_path}/strings/0x409/serialnumber'], check=True)
            subprocess.run(['sudo', 'sh', '-c', f'echo "Raspberry Pi" > {gadget_path}/strings/0x409/manufacturer'], check=True)
            subprocess.run(['sudo', 'sh', '-c', f'echo "USB Gadget" > {gadget_path}/strings/0x409/product'], check=True)

            os.makedirs(f"{gadget_path}/configs/c.1", exist_ok=True)
            os.makedirs(f"{gadget_path}/functions/mass_storage.0", exist_ok=True)
            subprocess.run(['sudo', 'sh', '-c', f'echo 1 > {gadget_path}/functions/mass_storage.0/stall'], check=True)
            subprocess.run(['sudo', 'ln', '-s', f"{gadget_path}/functions/mass_storage.0", f"{gadget_path}/configs/c.1/"], check=True)

            subprocess.run(['sudo', 'sh', '-c', f'echo "$(ls /sys/class/udc)" > {gadget_path}/UDC'], check=True)
            
    def mount_to_gadget(self, mount_path, backing_file, lun_config_path):
        """
        Monta la carpeta local como un dispositivo USB utilizando gadget mode.
        """
        # Paso 1: Configurar el gadget USB si no está configurado
        self.configure_gadget()

        # Paso 2: Verificar si ya está montado
        if os.path.ismount(mount_path):
            print(f"{mount_path} ya está montado. Procediendo a desmontarlo...")
            subprocess.run(['sudo', 'umount', mount_path], check=True)

        # Paso 3: Actualizar configuración del gadget USB
        print(f"Actualizando configuración del gadget USB en {lun_config_path}...")
        with open(lun_config_path, "w") as lun_file:
            lun_file.write(backing_file)

        print("Operación completada con éxito.")