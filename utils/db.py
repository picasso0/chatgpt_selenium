from pymongo import MongoClient
import os
def get_db():
    client = MongoClient(os.getenv('MONGODB_URL'))
    db = client["chatgpt_selenium"] 
    return db