'''
Author: Aditya Ramanathan

Description: Schema for a deck in body of an endpoint.
'''

from pydantic import BaseModel
from typing import List

class Deck(BaseModel):
    name: str
    description: str