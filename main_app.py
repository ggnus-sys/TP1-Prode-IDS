from werkzeug.middleware.dispatcher import DispatcherMiddleware
from app_backend.app import app as backend_app
from flask import Flask

app = Flask(__name__)
app.wsgi_app = DispatcherMiddleware(backend_app.wsgi_app)

if __name__ == '__main__':
    app.run(port=5000, debug=True)