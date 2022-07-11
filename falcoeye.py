import os
import logging
from dotenv import load_dotenv
import requests
import logging 
from falcoeye_kubernetes import FalcoServingKube
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# login to backend
workflow_user = os.getenv("WORKFLOW_USER")
workflow_password = os.getenv("WORKFLOW_PASSWORD")

artifact_registry = os.getenv("ARTIFACT_REGISTRY")
if artifact_registry:
    FalcoServingKube.set_artifact_registry(artifact_registry)

backend_kube = FalcoServingKube("falcoeye-backend")
backend_server = backend_kube.get_service_address()
URL = f"http://{backend_server}"
 
payload =  {
        "email": workflow_user.strip(),
        "password": workflow_password.strip()
}
r = requests.post(f"{URL}/auth/login", json=payload)
assert "access_token" in r.json()
access_token = r.json()["access_token"]
os.environ["JWT_KEY"] = access_token

from app import create_app
app = create_app(os.getenv("FLASK_CONFIG") or "default")

if __name__ == "__main__":
    app.run()
