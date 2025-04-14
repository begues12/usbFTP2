from app.storage.storage_interface import StorageInterface
import dropbox

class DropboxStorage(StorageInterface):
    def __init__(self):
        self.dbx = None
        
    def connect(self, credentials):
        """
        Conecta a Dropbox utilizando las credenciales proporcionadas.
        """
        token = credentials.get('token')
        if not token:
            raise ValueError("El token de autenticación es obligatorio")
        self.dbx = dropbox.Dropbox(token)
        return "Conectado a Dropbox con éxito"

    def login(self, credentials):
        token = credentials.get('token')
        if not token:
            raise ValueError("El token de autenticación es obligatorio")
        self.dbx = dropbox.Dropbox(token)
        return "Conectado a Dropbox con éxito"

    def logout(self):
        self.dbx = None
        return "Sesión de Dropbox cerrada con éxito"

    def refresh(self):
        if not self.dbx:
            raise ConnectionError("No hay una conexión activa")
        return "Conexión de Dropbox refrescada con éxito"

    def upload_file(self, file_path, destination):
        with open(file_path, 'rb') as file:
            self.dbx.files_upload(file.read(), destination)
        return f"Archivo {file_path} subido a {destination}"

    def download_file(self, file_path, destination):
        metadata, response = self.dbx.files_download(file_path)
        with open(destination, 'wb') as file:
            file.write(response.content)
        return f"Archivo {file_path} descargado a {destination}"
    
    def list_files(self):
        """
        Lista los archivos y carpetas en el directorio raíz de Dropbox.
        """
        if not self.dbx:
            raise ConnectionError("No hay conexión activa a Dropbox")
        files = []
        for entry in self.dbx.files_list_folder('').entries:
            files.append(entry.name)
        return files