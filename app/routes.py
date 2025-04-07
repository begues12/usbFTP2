import subprocess
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'  # Cambia esto por una clave secreta segura

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/wifi', methods=['GET', 'POST'])
def wifi():
    networks = []
    error_message = None
    if request.method == 'POST':
        networks = scan_wifi()
        if not networks:
            error_message = 'No se encontraron redes Wi-Fi.'
    return render_template('wifi.html', networks=networks, error_message=error_message)

def scan_wifi():
    networks = []
    try:
        result = subprocess.run(['sudo', 'iwlist', 'scan'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        networks = parse_wifi_output(output)
    except Exception as e:
        networks = []
    return networks

def parse_wifi_output(output):
    networks = []
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("SSID"):
            if ':' in line:
                parts = line.split(':', 1)
                ssid = parts[1].strip() if len(parts) > 1 else ''
                networks.append(ssid)
    return networks
