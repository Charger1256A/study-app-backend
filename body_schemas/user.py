'''
Author: Aditya Ramanathan

Description: Schema for a user in body of an endpoint.
'''

from pydantic import BaseModel
from typing import List

class User(BaseModel):
    username: str
    password: str