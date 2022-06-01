""" Top level module

This module:

- Contains create_app()
- Registers extensions
"""
from flask import Flask

from config import config_by_name

from .api import api_bp
# Import extensions
# Import config
# from flask_restplus import Api
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])


    app.register_blueprint(api_bp, url_prefix="/api")

    return app
