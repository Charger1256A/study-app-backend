'''
Author: Aditya Ramanathan

Backend for study app.
'''

from fastapi import FastAPI

app = FastAPI()

# Template default route
@app.get("/")
async def root():
    return {"message": "Hello World"}