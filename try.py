
from pymongo import MongoClient
import os
import jwt
import datetime
from dotenv import load_dotenv
from config import SECRET_KEY

# load_dotenv()

# client = MongoClient(os.getenv('DB_URL'))
# db = client.get_database("test")
# users = db.get_collection("Registration")
# comics = db.get_collection("Comics")

# user = users.find_one({"email": "agam_be21@thapar.edu"})
# print(user['user_name'])

def generate_jwt(email, name, expires_delta: datetime.timedelta = datetime.timedelta(days=7)):
    payload = {
        'email': email,
        'name': name,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
        'iat': datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
  
    return token

print(generate_jwt("agam_be21@thapar.edu", "Agam"))