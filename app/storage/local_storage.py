from app.models.connection_model import Connection
import os
import json
import datetime

class LocalStorage(Connection):
    
    def __init__(self, id):
        """
        Inicializa el almacenamiento local con un ID de conexión.
        """
        connection = Connection.get_by_id(id)
        if not connection:
            raise ValueError(f"No se encontró una conexión con el ID {id}.")
        
        super().__init__()
        self.id             = connection.id
        self.name           = connection.name
        self.type           = connection.type
        self.credentials    = connection.credentials
        self.password_hash  = connection.password_hash
        self.base_path      = self.credentials.get('base_path', "") 
        
    def connect(self, token=None):
        """
        Comprueba el token ok
        """
        print(f"Conectado a LocalStorage en {self.base_path}")
    
    def test_connection(self):
        """"
        Si existe la carpeta base_path, se considera que la conexión es exitosa.
        """
        if os.path.exists(self.base_path):
            return 'mount'
        else:
            raise FileNotFoundError(f"La carpeta {self.base_path} no existe.")
    
    def disconnect(self):
        """
        Realiza las operaciones necesarias para desconectar LocalStorage.
        """
        if self.base_path and os.path.exists(self.base_path):
            print(f"Desmontando LocalStorage en {self.base_path}")

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
                "name"          : item,
                "is_dir"        : os.path.isdir(item_path),
                "size"          : os.path.getsize(item_path) if not os.path.isdir(item_path) else 0,
                "modified_time" : datetime.datetime.fromtimestamp(os.path.getmtime(item_path)).strftime("%d/%m/%Y %H:%M"),
                "path"          : os.path.relpath(item_path, self.base_path)
            })
        return files