from abc import ABC, abstractmethod

class StorageInterface(ABC):
    """
    Clase base para definir la interfaz común de almacenamiento.
    """

    @abstractmethod
    def login(self, credentials):
        """Inicia sesión en el servicio de almacenamiento."""
        pass

    @abstractmethod
    def logout(self):
        """Cierra sesión en el servicio de almacenamiento."""
        pass

    @abstractmethod
    def refresh(self):
        """Refresca la conexión al servicio de almacenamiento."""
        pass

    @abstractmethod
    def upload_file(self, file_path, destination):
        """Sube un archivo al servicio de almacenamiento."""
        pass

    @abstractmethod
    def download_file(self, file_path, destination):
        """Descarga un archivo del servicio de almacenamiento."""
        pass