import subprocess
from flask import Flask, render_template, request, flash

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'  # Cambia esto por una clave secreta segura

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/wifi', methods=['GET', 'POST'])
def wifi():
    networks = []
    if request.method == 'POST':
        networks = scan_wifi()
        if not networks:
            flash('No se encontraron redes Wi-Fi.', 'danger')
    return render_template('wifi.html', networks=networks)

def scan_wifi():
    networks = []
    try:
        result = subprocess.run(['sudo', 'iwlist', 'scan'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        networks = parse_wifi_output(output)
    except Exception as e:
        print(f'Error al escanear Wi-Fi: {e}')
    return networks

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
