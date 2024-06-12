'''
Author: Aditya Ramanathan
Description: contains utility function required for backend.
'''

import os
import hashlib

def hash_password(password: str):
    '''
    Given a password this function will return a hashed version of it.

    Args:
        password: the password to be hashed -> str

    Returns: hashed version of password -> bytes 

    '''
    salt = os.urandom(32)
    password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return password