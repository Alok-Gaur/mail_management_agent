from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

RELATIONAL_DB_URL = os.getenv("RELATIONAL_DB_URL")
VECTOR_DB_URL = os.getenv("VECTOR_DB_URL")


# Google Cloud Secrets
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

# JWT Secrets
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_TIME = int(os.getenv("ACCESS_TOKEN_EXPIRE_TIME", "600")) 


# AI Service Secrets
AGENT_MODEL = os.getenv("AGENT_MODEL")
AGENT_URL = os.getenv("AGENT_URL")