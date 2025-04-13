import argparse
from app import create_app

# Crear la instancia de la aplicación
app = create_app()

if __name__ == '__main__':
    # Configurar argparse para manejar argumentos de línea de comandos
    parser = argparse.ArgumentParser(description="Ejecutar la aplicación Flask")
    parser.add_argument('--port', type=int, default=5060, help='Puerto en el que se ejecutará la aplicación (por defecto: 5060)')
    args = parser.parse_args()

    # Ejecutar la aplicación Flask en el puerto especificado
    app.run(debug=True, host='0.0.0.0', port=args.port)