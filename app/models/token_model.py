from app.extensions import db
from datetime import datetime, timedelta
import secrets

class Token(db.Model):
    __tablename__ = 'tokens'

    id              = db.Column(db.Integer, primary_key=True)
    connection_id   = db.Column(db.Integer, db.ForeignKey('connections.id'), nullable=False)
    token           = db.Column(db.String(64), unique=True, nullable=False)
    expires_at      = db.Column(db.DateTime, nullable=False)

    @staticmethod
    def generate_token(connection_id, expiration_minutes=30):
        """
        Genera un token con una fecha de expiración en UTC.
        """
        token       = secrets.token_hex(32)
        expires_at  = datetime.utcnow() + timedelta(minutes=expiration_minutes)
        new_token   = Token(connection_id=connection_id, token=token, expires_at=expires_at)
        db.session.add(new_token)
        db.session.commit()
        return token
    
    @staticmethod
    def validate_token(connection_id, token):
        """
        Get the token from the database and check if it is valid filter by connection_id 
        """
        token_entry = Token.query.filter_by(connection_id=connection_id, token=token).first()

        if not token_entry:
            return None
        
        if token_entry.expires_at < datetime.utcnow():
            db.session.delete(token_entry)
            db.session.commit()
            return None
        
        return token_entry