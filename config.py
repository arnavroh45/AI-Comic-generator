import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
SEGMIND_API_KEY = os.getenv('SEGMIND_API_KEY')
SEGMIND_URL = os.getenv('SEGMIND_URL')
CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')
LLM_MODEL = os.getenv("LLM_MODEL")
TEXT_TO_IMAGE_MODEL = os.getenv("TEXT_TO_IMAGE_MODEL")
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")

client = MongoClient(os.getenv('DB_URL'))
db = client.get_database("test")
users = db.get_collection("Registration")
comics = db.get_collection("Comics")

