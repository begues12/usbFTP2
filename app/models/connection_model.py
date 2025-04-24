from app.extensions import db  # Importa la instancia de SQLAlchemy desde extensions.py
from app.models.base_model import BaseModel  # Importa el modelo base
from werkzeug.security import generate_password_hash, check_password_hash  # Para manejar contraseñas de forma segura
from app.models.token_model import Token  # Importa el modelo de token para validación
from cryptography.fernet import Fernet
import os, json, base64  # Importa módulos necesarios para la encriptación y manejo de archivos

class Connection(BaseModel):
    __tablename__ = 'connections'
    
    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(100), nullable=False)
    type            = db.Column(db.String(50), nullable=False)  # Ejemplo: 'ftp', 'dropbox', 'google_drive'
    credentials     = db.Column(db.JSON, nullable=False)  # Almacena credenciales como JSON
    password_hash   = db.Column(db.String(255), nullable=True)  # Almacena la contraseña encriptada
    
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", base64.b64encode(os.urandom(32)).decode())  # Clave de encriptación base64 de 32 bytes

    if ENCRYPTION_KEY is None or len(ENCRYPTION_KEY) != 44:  # 44 caracteres base64 = 32 bytes decodificados
        raise ValueError("La clave de encriptación (ENCRYPTION_KEY) no es válida. Debe ser una cadena base64 de 32 bytes.")

    fernet = Fernet(ENCRYPTION_KEY)
    
    def __init__(self, id=None):
        """Inicializa la conexión con un ID opcional."""
        super().__init__()
        self.id = id
        self.name = ""
        self.type = ""
        self.credentials = {}
        self.password_hash = None
    
    def set_new(self, name, type, credentials, password=None):
        """Establece una nueva conexión con nombre, tipo y credenciales."""
        self.name = name
        self.type = type
        self.credentials = credentials
        if password:
            self.set_password(password)
    
    def set_credentials(self, credentials):
        """
        Guarda las credenciales directamente como JSON.
        """
        self.credentials = credentials  # Almacena el diccionario directamente

    def get_credentials(self):
        """
        Devuelve las credenciales como un objeto JSON.
        """
        return json.loads(self.credentials) if self.credentials else {}
    
    def set_password(self, password):
        """Encripta y guarda la contraseña."""
        self.password_hash = generate_password_hash(password)
    
    def has_password(self):
        """Verifica si la conexión tiene una contraseña establecida."""
        # Print paswword hash for debugging
        return self.password_hash is not None and self.password_hash != ''
    
    def check_password(self, password):
        """Verifica si la contraseña proporcionada es correcta."""
        stored_password_hash = self.password_hash
        if not stored_password_hash:
            return False
        return check_password_hash(stored_password_hash, password)
    
    def validate_token(self, token):
        """
        Valida si el token proporcionado es válido y no ha expirado.
        """
        token_entry = Token.validate_token(self.id, token)
        if not token_entry:
            return False
        return token_entry.connection_id == self.id
    
    def generate_token(self):
        """
        Genera un nuevo token para la conexión.
        """
        return Token.generate_token(self.id)
        
    
    def save(self):
        """Guarda la conexión en la base de datos. Si ya existe, la actualiza."""
        if self.id is None:
            db.session.add(self)
        else:
            existing_connection = Connection.query.get(self.id)
            if existing_connection:
                existing_connection.name = self.name
                existing_connection.type = self.type
                existing_connection.credentials = self.credentials
                existing_connection.password_hash = self.password_hash
            else:
                db.session.add(self)
        db.session.commit()

    def delete(self):
        """Elimina la conexión de la base de datos."""
        if self.id is None:
            raise ValueError("No se puede eliminar una conexión sin ID.")
        
        connection = Connection.query.get(self.id)
        if connection:
            db.session.delete(connection)
            db.session.commit()
        else:
            raise ValueError(f"No se encontró una conexión con ID {self.id}.")
        

    @staticmethod
    def get_all():
        """Obtiene todas las conexiones guardadas en la base de datos.
        Genera los modelos pertinentes para cada tipo de conexión."""
        connections = Connection.query.all()
        connection_models = []
        for connection in connections:
            if connection.type == 'local':
                from app.storage.local_storage import LocalStorage
                connection_models.append(LocalStorage(connection.id))
            elif connection.type == 'ftp':
                from app.storage.ftp_storage import FTPStorage
                connection_models.append(FTPStorage(connection.id))
            # Agregar más tipos de conexión según sea necesario
        return connection_models
    
    @staticmethod
    def get_by_id(connection_id):
        """Obtiene una conexión por su ID."""
        if connection_id is None:
            raise ValueError("El ID de conexión no puede ser None.")
        return Connection.query.get(connection_id)