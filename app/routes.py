from flask import Flask, render_template, request, flash
from app import app
import os
import subprocess

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/wifi')
def wifi():
    networks = scan_wifi()
    return render_template('wifi.html', networks=networks)


@app.route('/wifi', methods=['GET', 'POST'])
def wifi():
    networks = None
    error_message = None
    if request.method == 'POST':
        networks = scan_wifi()
        if networks is None:
            error_message = 'No se encontraron redes Wi-Fi.'
    return render_template('wifi.html', networks=networks, error_message=error_message)


def scan_wifi():
    try:
        # Ejecuta el comando para escanear redes Wi-Fi
        result = subprocess.run(['sudo', 'iwlist', 'scan'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        networks = parse_wifi_output(output)
        if not networks:
            return None
        return networks
    except Exception as e:
        return str(e)

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
