'''
Author: Aditya Ramanathan

Description: Backend for study app.
'''

from fastapi import FastAPI, Response, Request
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from starlette.middleware.sessions import SessionMiddleware
from typing import List
from bson.objectid import ObjectId
from fastapi.middleware.cors import CORSMiddleware



from body_schemas.user import User
from body_schemas.deck import Deck
from body_schemas.cards import Cards
from utilities import hash_password, passwords_match

load_dotenv()

# atlas url for connection
CONNECTION_STRING = os.getenv('MONGODB_CONNECTION')

# create a connection using MongoClient.
client = MongoClient(CONNECTION_STRING)
db = client["study-app"]

app = FastAPI()

origins = [
    "http://localhost:5173",  # React app
    "https://study-app-frontend.vercel.app"
    # add any other origins that need to access your API
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# creates session
SESSION_KEY = os.getenv("SESSION_KEY")
app.add_middleware(SessionMiddleware, secret_key=SESSION_KEY,  https_only=True,  same_site="None")

@app.get("/")
async def root():
    '''
    Template default route
    '''
    return {"message": "Study App Default Route"}


@app.post("/signup", status_code=201)
async def signup(user: User, response: Response, request: Request):
    '''
    Allows users to signup
    '''
    # gets data from body
    username = user.username
    password = user.password

    password, salt = hash_password(password)

    # gets users collection
    users_collection = db["users"]

    # return bad status code if username or password does not exist
    if username == "" or password == "":
        response.status_code = 400
        return {"message": "username and password must exist."}

    # return bad status code if user already exists
    existing_user = users_collection.find_one({ "username": username })
    if existing_user != None:
        response.status_code = 400
        return {"message": "user already has an account"}

    # creates object to insert into collection
    new_user = {
        "username": username,
        "password": password,
        "salt": salt,
        "decks": [],
    }
    # inserts object into collection
    new_user = users_collection.insert_one(new_user)

    # log user in
    request.session["user"] = str(new_user.inserted_id)

    # TODO: return good status code if successful
    return {"message": "user successfully created."}

@app.post("/login", status_code=200)
async def login(user: User, response: Response, request: Request):
    '''
    Allows users to login
    '''
    # gets data from body
    username = user.username
    password = user.password


    # gets user collection
    users_collection = db["users"]

    # return bad status code if username or password does not exist
    if username == "" or password == "":
        response.status_code = 400
        return {"message": "username and password must exist."}

    # return bad status code if username or password do not match
    existing_user = users_collection.find_one({ "username": username })
    if existing_user == None or not passwords_match(password, existing_user["password"], existing_user["salt"]):
        response.status_code = 400
        return {"message": "incorrect credentials."}


    request.session["user"] = str(existing_user["_id"])

    return {"message": "user signed in."}

    
@app.post("/logout", status_code=200)
async def logout(response: Response, request: Request):
    '''
    Allows users to logout
    '''
    # check if a user is logged in
    if "user" not in request.session:
        response.status_code = 400
        return {"message": "no user logged in."}

    # delete user from session
    del request.session["user"]
    return {"message": "user logged out."}

@app.post("/create-deck", status_code=200)
async def create_deck(deck: Deck, response: Response, request: Request):
    '''
    Allows user to create a deck
    '''
    # check if user is logged in
    if "user" not in request.session:
        response.status_code = 400
        return {"message": "No user logged in."}

    # get data from body
    name = deck.name

    # checks if name exists
    if name == "":
        response.status_code = 400
        return {"message": "deck must have a name."}

    # get decks collection
    decks_collection = db["decks"]

    # create the deck
    new_deck = {
        "name": deck.name,
        "description": deck.description,
        "cards": []
    }

    # insert deck into database
    deck = decks_collection.insert_one(new_deck)
    deck_id = deck.inserted_id

    # add deck to user
    users_collection = db["users"]
    user_id = request.session["user"]
    users_collection.update_one(
        {"_id": ObjectId(user_id)},  # query
        {"$push": {"decks": deck_id}}  # update
    )
    return {"message": "deck created.", "deck_id": str(deck_id)}

@app.post("/set-cards", status_code=200)
async def set_cards(cards: Cards, response: Response, request: Request):
    '''
    Allows users to set cards in a deck.
    '''
    # check if user is logged in
    if "user" not in request.session:
        response.status_code = 400
        return {"message": "No user logged in."}

    # get data from body
    deck_id = cards.deck_id
    cards_list = cards.cards

    # check if deck_id exists
    if deck_id == "":
        response.status_code = 400
        return {"message": "Invalid deck."}

    # check if deck is created
    decks_collection = db["decks"]
    deck = None
    try:
        deck = decks_collection.find_one({ "_id": ObjectId(deck_id) })
    except:
        response.status_code = 400
        return {"message": "Invalid deck."}

    # check if deck is current users deck
    users_collection = db["users"]
    user = users_collection.find_one({ "_id": ObjectId(request.session["user"]) })
    if ObjectId(deck_id) not in user["decks"]:
        response.status_code = 400
        return {"message": "Invalid deck."}

    # remove all cards currently in deck
    cards_collection = db["cards"]
    cards_collection.delete_many({"deck_id": deck_id})

    # inserts new ards into cards collection
    parsed_cards_list = []
    for card in cards_list:
        cards_obj = {
            "term": card.term,
            "definition": card.definition,
            "deck_id": deck_id,
        }

        parsed_cards_list.append(cards_obj)

    card_ids = cards_collection.insert_many(parsed_cards_list).inserted_ids

    # add new cards to deck collection
    deck["cards"] = card_ids
    decks_collection.update_one(
        {"_id": ObjectId(deck['_id'])},  # filter
        {"$set": {"cards": card_ids}}  # update
    )

    return { "message": "cards have been set." }

@app.get("/get-decks", status_code=200)
async def get_decks(response: Response, request: Request):
    '''
    Allows users to get their decks
    '''
    # check if user is logged in
    if "user" not in request.session:
        response.status_code = 400
        return {"message": "No user logged in."}

    # get decks
    user_id = ObjectId(request.session["user"])
    users_collection = db["users"]
    user = users_collection.find_one({ "_id": user_id })
    deck_ids = user["decks"]
    decks_collection = db["decks"]
    decks = []
    for deck_id in deck_ids:
        deck = decks_collection.find_one({ "_id": deck_id })
        deck_obj = {
            "id": str(deck_id),
            "name": deck["name"],
            "description": deck["description"],
        }
        decks.append(deck_obj)

    return decks

@app.get("/get-cards/{deck_id}", status_code=200)
def get_cards(deck_id, response: Response, request: Request):
    '''
    Allows users to get cards for a deck
    '''
    # check if user is logged in
    if "user" not in request.session:
        response.status_code = 400
        return {"message": "No user logged in."}
    
    try:
        deck_id = ObjectId(deck_id)
    except:
        response.status_code = 400
        return {"message": "Invalid deck."}

    # check if deck is current users
    user_id = ObjectId(request.session["user"])
    users_collection = db["users"]
    user = users_collection.find_one({ "_id": user_id })
    deck_ids = user["decks"]
    if deck_id not in deck_ids:
        response.status_code = 400
        return {"message": "Invalid deck."}

    # get the deck
    decks_collection = db["decks"]
    deck = decks_collection.find_one({ "_id": deck_id })

    # get each card
    card_ids = deck["cards"]
    cards_collection = db["cards"]
    cards = []
    for card_id in card_ids:
        card = cards_collection.find_one({ "_id": card_id })
        card["id"] = str(card["_id"])
        del card["_id"]
        cards.append(card)

    return cards
    

    
    
