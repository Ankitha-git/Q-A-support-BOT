import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Website to crawl
BASE_URL = "https://docs.python.org/3/tutorial/"  # Example - you can change this
MAX_PAGES = 20  # Limit pages to crawl

# Embedding settings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Free, local model
CHUNK_SIZE = 500  # Characters per chunk
CHUNK_OVERLAP = 50  # Overlap between chunks

# Vector Database
COLLECTION_NAME = "website_docs"
PERSIST_DIRECTORY = "./chroma_db"

# API settings
API_HOST = "0.0.0.0"
API_PORT = 8000

# OpenAI (optional - for better quality answers)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
USE_OPENAI = False  # Set to True if you want to use OpenAI