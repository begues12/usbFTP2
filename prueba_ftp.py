from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

def start_ftp_server(host='127.0.0.1', port=2121, user='user', password='password', directory='./ftp_root'):
    """
    Inicia un servidor FTP básico.

    :param host: Dirección IP del servidor (por defecto: 127.0.0.1)
    :param port: Puerto del servidor FTP (por defecto: 2121)
    :param user: Nombre de usuario para autenticación
    :param password: Contraseña para autenticación
    :param directory: Directorio raíz para el servidor FTP
    """
    # Crear un autorizer para manejar usuarios
    authorizer = DummyAuthorizer()

    # Añadir un usuario con permisos de lectura/escritura
    authorizer.add_user(user, password, directory, perm='elradfmwMT')  # Permisos: todo permitido
    # Añadir un usuario anónimo (opcional, solo lectura)
    # authorizer.add_anonymous(directory, perm='elr')

    # Configurar el manejador FTP
    handler = FTPHandler
    handler.authorizer = authorizer

    # Configurar el servidor
    server = FTPServer((host, port), handler)

    print(f"Servidor FTP iniciado en {host}:{port}")
    print(f"Usuario: {user}, Contraseña: {password}")
    print(f"Directorio raíz: {directory}")

    # Iniciar el servidor
    server.serve_forever()

if __name__ == '__main__':
    # Configuración del servidor
    start_ftp_server(
        host='127.0.0.1',  # Cambia a '0.0.0.0' para aceptar conexiones externas
        port=2121,
        user='admin',
        password='admin123',
        directory='./ftp_root'  # Cambia al directorio que desees usar como raíz
    )