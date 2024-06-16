from dotenv import load_dotenv
import os


load_dotenv()

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

PrivateKey = "certs/private.pem"
PublicKey = "certs/public.pem"
algorithm: str = "RS256"


API_KEYS = {
    os.getenv("API_KEY_1"): "Key1",
    os.getenv("API_KEY_2"): "Key2",
    os.getenv("api_key_for_jinja"): "Key2",
}

api_key = os.getenv("api_key_for_jinja")