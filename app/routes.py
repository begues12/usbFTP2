import os
import subprocess
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from ftplib import FTP
import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

app = Flask(__name__)
app.secret_key = os.urandom(24)
Bootstrap(app)

# Ruta de inicio
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para escanear redes Wi-Fi
@app.route('/wifi', methods=['GET', 'POST'])
def wifi():
    networks = []
    error_message = None
    if request.method == 'POST':
        networks = scan_wifi()
        if not networks:
            error_message = 'No se encontraron redes Wi-Fi.'
    return render_template('wifi.html', networks=networks, error_message=error_message)

# Función para escanear redes Wi-Fi
def scan_wifi():
    try:
        result = subprocess.run(['sudo', 'iwlist', 'scan'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        networks = parse_wifi_output(output)
        return networks
    except Exception as e:
        return []

# Función para procesar la salida del escaneo de Wi-Fi
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

# Ruta para gestionar conexiones FTP
@app.route('/ftp', methods=['GET', 'POST'])
def ftp():
    if request.method == 'POST':
        server = request.form['server']
        username = request.form['username']
        password = request.form['password']
        try:
            ftp = FTP(server)
            ftp.login(user=username, passwd=password)
            files = ftp.nlst()
            ftp.quit()
            return render_template('ftp.html', files=files)
        except Exception as e:
            flash(f'Error al conectar al servidor FTP: {e}', 'danger')
    return render_template('ftp.html', files=None)

# Ruta para gestionar conexiones a Google Drive
@app.route('/drive', methods=['GET'])
def drive():
    try:
        creds, project = google.auth.default()
        service = build('drive', 'v3', credentials=creds)
        results = service.files().list(pageSize=10, fields="files(id, name)").execute()
        files = results.get('files', [])
        return render_template('drive.html', files=files)
    except Exception as e:
        flash(f'Error al conectar a Google Drive: {e}', 'danger')
        return render_template('drive.html', files=None)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
