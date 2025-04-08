from flask import Flask

app = Flask(__name__)

# Importa y registra el blueprint
from app.routes import home_routes, wifi_routes, storage_routes
app.register_blueprint(wifi_routes.wifi_bp, url_prefix='/wifi')
app.register_blueprint(home_routes.home_bp, url_prefix='/home')
app.register_blueprint(storage_routes.storage_bp, url_prefix='/storage')