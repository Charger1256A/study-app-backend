'''
Author: Aditya Ramanathan
Description: contains utility function required for backend.
'''

import os
import hashlib

def hash_password(password: str, salt=None):
    '''
    Given a password this function will return a hashed version of it. If no salt is provided a new salt will be generated.

    Args:
        password: the password to be hashed -> str
        salt: the salt used in the hash function -> bytes

    Returns: 
        - hashed version of password -> bytes 
        - salt -> bytes

    '''
    if salt == None:
        salt = os.urandom(32)
    
    password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return password, salt

def passwords_match(password: str, hashed_password: bytes, salt: bytes):
    '''
    Checks if given password matches hashed password

    Args:
        password: the password to be hashed -> str
        hashed_password: the hashed password to compare password with
        salt: the salt used to hash password

    Returns: true if passwords match, false otherwise -> bool
    '''
    return hash_password(password, salt)[0] == hashed_password