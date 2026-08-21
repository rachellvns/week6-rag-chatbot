from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.environ["ANTHROPIC_API_KEY"]
BASE_URL = os.environ["ANTHROPIC_BASE_URL"]
MODEL = "claude-sonnet-4-6"

EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
QDRANT_PATH = "./qdrant_data"
COLLECTION_NAME = "corpus"