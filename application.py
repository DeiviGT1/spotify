from flask import Flask

# Se crea una instancia de la aplicación Flask
application = Flask(__name__, template_folder='templates', static_url_path="/static")

# Se importan los módulos de la aplicación
from controllers import mod

# Se registran los módulos de la aplicación en la instancia de la aplicación Flask
application.register_blueprint(mod)

if __name__ == '__main__':
    # Se inicia el servidor web de Flask
    application.run()
    # application.run(host='0.0.0.0', port=80, debug=False)