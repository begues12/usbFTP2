from app.models.base_model import db, BaseModel

class Connection(BaseModel):
    __tablename__ = 'connections'

    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # Ejemplo: 'ftp', 'dropbox', 'google_drive'
    credentials = db.Column(db.JSON, nullable=False)  # Almacena credenciales como JSON

    def __init__(self, name, type, credentials):
        self.name = name
        self.type = type
        self.credentials = credentials

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