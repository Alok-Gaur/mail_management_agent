from dotenv import load_dotenv
import os

load_dotenv()

RELATIONAL_DB_URL = os.getenv("RELATIONAL_DB_URL")
VECTOR_DB_URL = os.getenv("VECTOR_DB_URL")
