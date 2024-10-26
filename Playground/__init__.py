import os
from flask import Flask
from Playground.blueprint.landing import landing
from Playground.blueprint.home import home
from Playground.blueprint.type import type
from Playground.blueprint.upload import upload
from Playground.blueprint.generated import generated

def create_app():
    app = Flask(__name__)
    UPLOAD_FOLDER = 'static/uploads'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    app.register_blueprint(landing)
    app.register_blueprint(home)
    app.register_blueprint(type)
    app.register_blueprint(upload)
    app.register_blueprint(generated)

    return app
