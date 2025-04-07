from flask import render_template
from app import app
import os

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/wifi')
def wifi():
    networks = scan_wifi()
    return render_template('wifi.html', networks=networks)

def scan_wifi():
    networks = []
    if os.name == 'nt':  # Windows
        # Comando para Windows
        command = 'netsh wlan show networks'
    else:  # Linux/Mac
        # Comando para Linux/Mac
        command = 'nmcli dev wifi list'
    
    result = os.popen(command).read()
    networks = parse_wifi_output(result)
    return networks

def parse_wifi_output(output):
    networks = []
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("SSID"):  # Solo procesa las líneas que contienen información del SSID
            # Verifica si la línea contiene ':' y divídela de manera segura
            if ':' in line:
                parts = line.split(':', 1)
                ssid = parts[1].strip() if len(parts) > 1 else ''
                networks.append(ssid)
    return networks

