
from flask import current_app as app

def get_model_server(model_name, model_version,run_if_down=True):
    if app.config["DEP_ENV"] == "grun":
        from .grun import get_service_server as gsa
        return gsa(model_name,model_version,run_if_down=run_if_down)
    elif app.config["DEP_ENV"] == "local":
        from .local import get_service_server as gsa
        return gsa(model_name,model_version,run_if_down=run_if_down)