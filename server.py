'''
Author: Aditya Ramanathan

Description: Backend for study app.
'''

from fastapi import FastAPI, Response, Request
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from starlette.middleware.sessions import SessionMiddleware

from body_schemas.user import User
from utilities import hash_password, passwords_match

load_dotenv()

# atlas url for connection
CONNECTION_STRING = os.getenv('MONGODB_CONNECTION')

# create a connection using MongoClient.
client = MongoClient(CONNECTION_STRING)
db = client["study-app"]

app = FastAPI()

# creates session
SESSION_KEY = os.getenv("SESSION_KEY")
app.add_middleware(SessionMiddleware, secret_key=SESSION_KEY)

@app.get("/")
async def root():
    '''
    Template default route
    '''
    return {"message": "Study App Default Route"}


@app.post("/signup", status_code=201)
async def signup(user: User, response: Response):
    '''
    Allows users to signup

    body:
        user: the user to create an account for -> User
    '''
    # gets data from body
    username = user.username
    password = user.password

    password, salt = hash_password(password)

    # gets user collection
    user_collection = db["users"]

    # return bad status code if username or password does not exist
    if username == "" or password == "":
        response.status_code = 400
        return {"message": "username and password must exist."}

    # return bad status code if user already exists
    existing_user = user_collection.find_one({"username": username})
    if existing_user != None:
        response.status_code = 400
        return {"message": "user already has an account"}

    # creates object to insert into collection
    test_user = {
        "username": username,
        "password": password,
        "salt": salt,
        "decks": [],
    }
    # inserts object into collection
    user_collection.insert_one(test_user)

    # TODO: return good status code if successful
    return {"message": "user successfully created."}

@app.post("/login", status_code=200)
async def login(user: User, response: Response, request: Request):
    '''
    Allows users to login

    body:
        user: the user to create an account for -> User
    '''
    # gets data from body
    username = user.username
    password = user.password

    # gets user collection
    user_collection = db["users"]

    # return bad status code if username or password does not exist
    if username == "" or password == "":
        response.status_code = 400
        return {"message": "username and password must exist."}

    # return bad status code if username or password do not match
    existing_user = user_collection.find_one({"username": username})
    if existing_user == None or not passwords_match(password, existing_user["password"], existing_user["salt"]):
        response.status_code = 400
        return {"message": "Incorrect credentials."}

    # check if user is already logged in
    if "user" in request.session:
        return {"message": "user already signed in."}

    
    # store user in session 
    request.session["user"] = existing_user["username"]
    return {"message": "user signed in."}

    

    