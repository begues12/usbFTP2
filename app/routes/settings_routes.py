from flask import Blueprint, render_template, request, jsonify

settings_bp = Blueprint('settings', __name__)

# Configuración simulada (puedes reemplazar esto con una base de datos o archivo de configuración)
app_settings = {
    "usb_folder": "/media/usb",
    "theme": "light",
    "language": "es"
}

@settings_bp.route('/', methods=['GET'])
def index():
    """
    Muestra la página de configuración.
    """
    return render_template('settings.html', settings=app_settings)

@settings_bp.route('/update', methods=['POST'])
def update_settings():
    """
    Actualiza las configuraciones de la aplicación.
    """
    data = request.json
    for key, value in data.items():
        if key in app_settings:
            app_settings[key] = value
    return jsonify({"message": "Configuraciones actualizadas con éxito", "settings": app_settings}), 200