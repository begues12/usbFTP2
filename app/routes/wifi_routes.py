from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
import subprocess

wifi_bp = Blueprint('wifi', __name__)

# Ruta para listar redes Wi-Fi
@wifi_bp.route('/list', methods=['GET', 'POST'])
def list_wifi():
    networks = []
    if request.method == 'POST':
        networks = scan_wifi()
        if not networks:
            flash('No se encontraron redes Wi-Fi.', 'danger')
    return render_template('wifi.html', networks=networks)

# Ruta para conectar a una red Wi-Fi
@wifi_bp.route('/connect', methods=['POST'])
def connect_wifi():
    ssid = request.form.get('ssid')
    password = request.form.get('password')
    if not ssid or not password:
        flash('SSID y contraseña son obligatorios.', 'danger')
        return redirect(url_for('wifi.list_wifi'))
    success = connect_to_wifi(ssid, password)
    if success:
        flash(f'Conectado a {ssid} con éxito.', 'success')
    else:
        flash(f'Error al conectar a {ssid}.', 'danger')
    return redirect(url_for('wifi.list_wifi'))

# Ruta para eliminar una red guardada
@wifi_bp.route('/remove', methods=['POST'])
def remove_wifi():
    ssid = request.form.get('ssid')
    if not ssid:
        flash('SSID es obligatorio para eliminar una red.', 'danger')
        return redirect(url_for('wifi.list_wifi'))
    success = remove_saved_wifi(ssid)
    if success:
        flash(f'Red {ssid} eliminada con éxito.', 'success')
    else:
        flash(f'Error al eliminar la red {ssid}.', 'danger')
    return redirect(url_for('wifi.list_wifi'))

# Ruta para guardar configuraciones de red
@wifi_bp.route('/save', methods=['POST'])
def save_wifi():
    ssid = request.form.get('ssid')
    password = request.form.get('password')
    if not ssid or not password:
        flash('SSID y contraseña son obligatorios para guardar la red.', 'danger')
        return redirect(url_for('wifi.list_wifi'))
    success = save_wifi_config(ssid, password)
    if success:
        flash(f'Red {ssid} guardada con éxito.', 'success')
    else:
        flash(f'Error al guardar la red {ssid}.', 'danger')
    return redirect(url_for('wifi.list_wifi'))


@wifi_bp.route('/list_wifi_ajax', methods=['GET'])
def list_wifi_ajax():
    networks = scan_wifi()  # Función que escanea redes Wi-Fi
    return jsonify({'networks': networks})

# Función para escanear redes Wi-Fi
def scan_wifi():
    networks = []
    try:
        result = subprocess.run(['sudo', 'iwlist', 'scan'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        networks = parse_wifi_output(output)
    except Exception as e:
        print(f'Error al escanear Wi-Fi: {e}')
    return networks

# Función para conectar a una red Wi-Fi
def connect_to_wifi(ssid, password):
    try:
        # Comando para conectarse a una red Wi-Fi (ejemplo para sistemas Linux)
        subprocess.run(['nmcli', 'dev', 'wifi', 'connect', ssid, 'password', password], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f'Error al conectar a la red Wi-Fi: {e}')
        return False

# Función para eliminar una red guardada
def remove_saved_wifi(ssid):
    try:
        # Comando para eliminar una red guardada (ejemplo para sistemas Linux)
        subprocess.run(['nmcli', 'connection', 'delete', ssid], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f'Error al eliminar la red Wi-Fi: {e}')
        return False

# Función para guardar configuraciones de red
def save_wifi_config(ssid, password):
    try:
        # Comando para guardar una red Wi-Fi (ejemplo para sistemas Linux)
        subprocess.run(['nmcli', 'connection', 'add', 'type', 'wifi', 'con-name', ssid, 'ifname', '*', 'ssid', ssid, 'wifi-sec.key-mgmt', 'wpa-psk', 'wifi-sec.psk', password], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f'Error al guardar la red Wi-Fi: {e}')
        return False

# Función para analizar la salida del escaneo Wi-Fi
def parse_wifi_output(output):
    networks = []
    current_network = None
    for line in output.splitlines():
        line = line.strip()
        if line.startswith('Cell'):
            if current_network:
                networks.append(current_network)
            current_network = {}
        elif 'ESSID' in line:
            ssid = line.split('ESSID:')[1].strip().replace('"', '')
            current_network['SSID'] = ssid
        elif 'Signal level' in line:
            signal = line.split('Signal level=')[1].split(' ')[0].strip()
            current_network['Signal'] = signal
    if current_network:
        networks.append(current_network)
    return networks