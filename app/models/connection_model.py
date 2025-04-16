from app.extensions import db  # Importa la instancia de SQLAlchemy desde extensions.py
from app.models.base_model import BaseModel  # Importa el modelo base
from werkzeug.security import generate_password_hash, check_password_hash  # Para manejar contraseñas de forma segura
from app.models.token_model import Token  # Importa el modelo de token para validación

class Connection(BaseModel):
    __tablename__ = 'connections'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # Ejemplo: 'ftp', 'dropbox', 'google_drive'
    credentials = db.Column(db.JSON, nullable=False)  # Almacena credenciales como JSON
    password_hash = db.Column(db.String(255), nullable=True)  # Almacena la contraseña encriptada
    
    def __init__(self, name, type, credentials):
        self.name = name
        self.type = type
        self.credentials = credentials
        self.password_hash = None  # Inicializa la contraseña como None
    
    def set_password(self, password):
        """Encripta y guarda la contraseña."""
        self.password_hash = generate_password_hash(password)

    def has_password(self):
        """Verifica si la conexión tiene una contraseña establecida."""
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
        token_entry = Token.validate_token(token)
        if not token_entry:
            return False
        return token_entry.connection_id == self.id
    
    def save(self):
        """Guarda la conexión en la base de datos."""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Elimina la conexión de la base de datos."""
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all():
        """Obtiene todas las conexiones guardadas en la base de datos."""
        return Connection.query.all()
    
    @staticmethod
    def get_by_id(connection_id):
        """Obtiene una conexión por su ID."""
        return Connection.query.get(connection_id)