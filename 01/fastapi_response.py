"""
Response Model - Return Type

"""

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class UserDeatils(BaseModel):
    name: str
    occupation: str
    experience: int
    past_companies: list[str]


@app.get("/")
def response():
    return "Hello"
