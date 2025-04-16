from flask import Flask
from app.extensions import db, socketio  # Importar db y socketio desde extensions.py
from app.routes.storage_routes import storage_bp
from app.routes.home_routes import home_bp
from app.routes.wifi_routes import wifi_bp
from app.routes.settings_routes import settings_bp

def create_app():
    app = Flask(__name__)

    # Configuración de la base de datos
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usbftp2.db'  # Cambia esto según tu base de datos
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializar SQLAlchemy
    db.init_app(app)

    # Inicializar SocketIO
    socketio.init_app(app)

    # Registrar blueprints
    app.register_blueprint(storage_bp, url_prefix='/storage')
    app.register_blueprint(home_bp)
    app.register_blueprint(wifi_bp, url_prefix='/wifi')
    app.register_blueprint(settings_bp, url_prefix='/settings')

    # Crear tablas si no existen
    with app.app_context():
        db.create_all()

    return app