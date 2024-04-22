from flask import Flask
from flask_cors import CORS
import logging
import os
from .app_blueprint import bp

__version__ = "0.2.12"




class BaseConfig(object):
    DEBUG = False
    TESTING = False
    HOME = os.path.expanduser("~")
    CORS_HEADERS = 'Content-Type'
    SECRET_KEY = '1d94e52c-1c89-4515-b87a-f48cf3cb7f0b'
    LOGGING_LEVEL = logging.DEBUG
    JSON_SORT_KEYS = False


class DeploymentWithRedisConfig(BaseConfig):
    """Deployment configuration with Redis."""
    USE_REDIS_JOBS = True
    REDIS_HOST = os.environ.get('REDIS_SERVICE_HOST')
    REDIS_PORT = os.environ.get('REDIS_SERVICE_PORT')
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
    REDIS_URL = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0'


def create_app(test_config=None):
    app = Flask(__name__)
    CORS(app, expose_headers='WWW-Authenticate')

    configure_app(app)

    if test_config is not None:
        app.config.update(test_config)

    app.register_blueprint(bp)
    app.url_map.strict_slashes = False

    return app

def configure_app(app):

    # Load logging scheme from config.py
    app_settings = os.getenv('APP_SETTINGS')
    if not app_settings:
        app.config.from_object(BaseConfig)
    else:
        app.config.from_object(app_settings)


