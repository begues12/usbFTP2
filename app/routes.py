from flask import Blueprint, render_template, request, redirect, url_for, flash
from .wifi import connect_to_wifi

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/configure', methods=['POST'])
def configure():
    ssid = request.form.get('ssid')
    password = request.form.get('password')

    if not ssid or not password:
        flash("Debe completar todos los campos")
        return redirect(url_for('main.index'))

    success, message = connect_to_wifi(ssid, password)

    if success:
        return "WiFi conectado correctamente. El sistema cambiará de red..."
    else:
        return f"Error al conectar: {message}", 500
