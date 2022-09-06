
from flask import current_app as app

def get_model_server(model_name, model_version,protocol,run_if_down=True):
    if app.config["DEPLOYMENT"] == "gcloud":
        from .grun import get_service_server as gsa
        return gsa(model_name,model_version,protocol,run_if_down=run_if_down)
    elif app.config["DEPLOYMENT"] == "local":
        from .local import get_service_server as gsa
        return gsa(model_name,model_version,protocol,run_if_down=run_if_down)
    
    elif app.config["DEPLOYMENT"] == "k8s":
        from .k8s import get_service_server as gsa
        return gsa(model_name,model_version,protocol,run_if_down=run_if_down)