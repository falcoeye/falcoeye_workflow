import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Change the secret key in production run.
    SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(24))
    DEBUG = False

    # JWT Extended config
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", os.urandom(24))

    JWT_HEADER_NAME = os.environ.get("JWT_HEADER_NAME", "X-API-KEY")
    JWT_HEADER_TYPE = os.environ.get("JWT_HEADER_TYPE")

    # Set the token to expire every week
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

    # flask restx settings
    SWAGGER_UI_DOC_EXPANSION = "list"

    # Streamer config
    STREAMER_HOST = os.environ.get("STREAMER_HOST", "http://127.0.0.1:5000")
    WORKFLOW_HOST = os.environ.get("WORKFLOW_HOST", "http://127.0.0.1:7000")
    ANALYSIS_STORAGE = f"{basedir}/../faloceye_storage/"
        


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(basedir, "data-dev.sqlite")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # temp directory for data
    TEMPORARY_DATA_PATH = f"{basedir}/data/"

    # Add logger


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    # In-memory SQLite for testing
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # temp directory for data
    TEMPORARY_DATA_PATH = f"{basedir}/data/"


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(basedir, "data.sqlite")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


config_by_name = dict(
    development=DevelopmentConfig,
    testing=TestingConfig,
    production=ProductionConfig,
    default=DevelopmentConfig,
)
