from ftplib import FTP
import logging

logging.basicConfig(level=logging.INFO)

class FTPStorage:
    def __init__(self):
        self.ftp = None

    def connect(self, credentials):
        """
        Conecta al servidor FTP utilizando las credenciales proporcionadas.
        """
        host = credentials.get('host')
        port = int(credentials.get('port'))
        username = credentials.get('username')
        password = credentials.get('password')

        logging.info(f"Intentando conectar al host: {host} en el puerto: {port}")

        if not host or not username or not password:
            raise ValueError("Faltan credenciales para la conexión FTP")

        # Establecer conexión al servidor FTP
        self.ftp = FTP()
        self.ftp.connect(host, port)  # Conectar al host y puerto
        self.ftp.login(user=username, passwd=password)

    def list_files(self):
        """
        Lista los archivos y carpetas en el directorio actual del servidor FTP.
        """
        if not self.ftp:
            raise ConnectionError("No hay conexión activa al servidor FTP")
        return self.ftp.nlst()

    def disconnect(self):
        """
        Cierra la conexión al servidor FTP.
        """
        if self.ftp:
            self.ftp.quit()
            self.ftp = None