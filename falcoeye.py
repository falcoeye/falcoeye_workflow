import os
import logging
from dotenv import load_dotenv
import requests
import logging 
from app.utils import get_service
from config import config_by_name
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


config_name = os.getenv("FLASK_CONFIG") or "default"
config = config_by_name[config_name]

URL = get_service("falcoeye-backend",deployment=config.DEPLOYMENT,config=config)
 

payload =  {
        "email": workflow_user.strip(),
        "password": workflow_password.strip()
}
r = requests.post(f"{URL}/auth/login", json=payload)
assert "access_token" in r.json()
access_token = r.json()["access_token"]
os.environ["JWT_KEY"] = f'JWT {access_token}'

from app import create_app
app = create_app(os.getenv("FLASK_CONFIG") or "default")

if __name__ == "__main__":
    app.run()
