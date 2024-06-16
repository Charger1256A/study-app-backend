'''
Author: Aditya Ramanathan

Description: Schema for a card in body of an endpoint.
'''

from pydantic import BaseModel
from typing import List

class Card(BaseModel):
    term: str
    definition: str

class Cards(BaseModel):
    deck_id: str
    cards: List[Card]

