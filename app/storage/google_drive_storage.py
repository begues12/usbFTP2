from app.storage.storage_interface import StorageInterface
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

class GoogleDriveStorage(StorageInterface):
    def __init__(self):
        self.gauth = None
        self.drive = None
        
    def connect(self, credentials):
        """
        Conecta a Google Drive utilizando las credenciales proporcionadas.
        """
        self.gauth = GoogleAuth()
        self.gauth.LoadCredentialsFile(credentials.get('credentials_file'))
        if not self.gauth.credentials:
            raise ValueError("No se pudieron cargar las credenciales")
        self.drive = GoogleDrive(self.gauth)
        return "Conectado a Google Drive con éxito"

    def disconnect(self, credentials):
        """
        Realiza las operaciones necesarias para desconectar GoogleDriveStorage.
        """
        print("Desconexión de Google Drive no requiere operaciones adicionales.")
    
    def login(self, credentials):
        self.gauth = GoogleAuth()
        self.gauth.LoadCredentialsFile(credentials.get('credentials_file'))
        if not self.gauth.credentials:
            raise ValueError("No se pudieron cargar las credenciales")
        self.drive = GoogleDrive(self.gauth)
        return "Conectado a Google Drive con éxito"

    def logout(self):
        self.gauth = None
        self.drive = None
        return "Sesión de Google Drive cerrada con éxito"

    def refresh(self):
        if not self.drive:
            raise ConnectionError("No hay una conexión activa")
        return "Conexión de Google Drive refrescada con éxito"

    def upload_file(self, file_path, destination):
        file = self.drive.CreateFile({'title': destination})
        file.SetContentFile(file_path)
        file.Upload()
        return f"Archivo {file_path} subido a {destination}"

    def download_file(self, file_path, destination):
        file = self.drive.CreateFile({'id': file_path})
        file.GetContentFile(destination)
        return f"Archivo {file_path} descargado a {destination}"