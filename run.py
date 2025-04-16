import argparse
from app import create_app
from app.extensions import socketio 
from flask_migrate import Migrate
from app.extensions import db

app = create_app()

migrate = Migrate(app, db)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Ejecutar la aplicación Flask")
    parser.add_argument('--port', type=int, default=5050, help='Puerto en el que se ejecutará la aplicación (por defecto: 5060)')
    args = parser.parse_args()

    socketio.run(app, debug=True, host='0.0.0.0', port=args.port)