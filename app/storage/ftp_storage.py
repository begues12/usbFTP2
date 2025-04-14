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

    def test_connection(self, credentials):
        """
        Prueba rápidamente la conexión al servidor FTP.
        """
        host = credentials.get('host')
        port = int(credentials.get('port', 21))  # Puerto predeterminado: 21
        username = credentials.get('username')
        password = credentials.get('password')

        logging.info(f"Probando conexión al host: {host} en el puerto: {port}")

        if not host or not username or not password:
            raise ValueError("Faltan credenciales para la conexión FTP")

        try:
            # Establecer conexión temporal para probar
            ftp = FTP()
            ftp.connect(host, port, timeout=5)  # Tiempo de espera corto para la prueba
            ftp.login(user=username, passwd=password)
            ftp.quit()
            logging.info("Conexión FTP exitosa")
            return True
        except (error_perm, error_temp, error_proto, error_reply) as e:
            logging.error(f"Error en la conexión FTP: {str(e)}")
            return False
        except Exception as e:
            logging.error(f"Error inesperado al conectar al servidor FTP: {str(e)}")
            return False

    def disconnect(self, credentials):
        """
        Realiza las operaciones necesarias para desconectar FTPStorage.
        """
        try:
            if self.ftp:
                self.ftp.quit()
                print("Conexión FTP cerrada correctamente.")
        except Exception as e:
            print(f"Error al desconectar FTP: {str(e)}")
        
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