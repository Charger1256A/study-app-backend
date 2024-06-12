'''
Author: Aditya Ramanathan

Backend for study app.
'''

from fastapi import FastAPI
import os
from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()

# atlas url for connection
CONNECTION_STRING = os.getenv('MONGODB_CONNECTION')

# Create a connection using MongoClient.
client = MongoClient(CONNECTION_STRING)
db = client["study-app"]

app = FastAPI()

'''
Template default route
'''
@app.get("/")
async def root():
    return {"message": "Study App Default Route"}

'''
Allows users to signup
'''
@app.post("/signup")
async def signup():
    user_collection = db["users"]
    test_user = {
        "username": "test_user",
        "password": "abcd",
        "decks": [],
    }
    user_collection.insert_one(test_user)
    pass