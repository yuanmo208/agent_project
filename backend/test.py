import chromadb
import os
from dotenv import load_dotenv
load_dotenv()
chroma_db_path = os.getenv("CHROMA_PATH")


client = chromadb.PersistentClient(path=chroma_db_path)