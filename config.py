import os
from datetime import timedelta
import logging
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    
    # flask restx settings
    SWAGGER_UI_DOC_EXPANSION = "list"
    BACKEND_HOST = os.environ.get("BACKEND_HOST", "http://127.0.0.1:5000")

    # file system interface
    FS_PROTOCOL = os.environ.get("FS_PROTOCOL", "file")
    

    if FS_PROTOCOL in ("gs", "gcs"):
        import gcsfs
        DEP_ENV = "grun"
        FS_TOKEN = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "cloud")
        FS_BUCKET = os.environ.get("FS_BUCKET", "")
        FS_PROJECT = os.environ.get("FS_PROJECT", "falcoeye")
        FS_PROJECT_ID = os.environ['FS_PROJECT_ID']
        FS_LOCATION = os.environ.get("FS_LOCATION", "")
        FS_OBJ = gcsfs.GCSFileSystem(project=FS_PROJECT, token=FS_TOKEN)
        FS_IS_REMOTE = True
        USER_ASSETS = os.environ.get("USER_ASSETS", f"{FS_BUCKET}/user-assets/")

    elif FS_PROTOCOL == "file":
        import fsspec
        DEP_ENV = "local"
        FS_OBJ = fsspec.filesystem(FS_PROTOCOL)
        FS_IS_REMOTE = False
        USER_ASSETS = os.environ.get("USER_ASSETS", f"{basedir}/tests/user-assets/")
    else:
        raise SystemError(f"support for {FS_PROTOCOL} has not been added yet")

   

        


class DevelopmentConfig(Config):
    DEBUG = True
    


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    # In-memory SQLite for testing
    PRESERVE_CONTEXT_ON_EXCEPTION = False


class ProductionConfig(Config):
    DEBUG = False
    


config_by_name = dict(
    development=DevelopmentConfig,
    testing=TestingConfig,
    production=ProductionConfig,
    default=DevelopmentConfig,
)
