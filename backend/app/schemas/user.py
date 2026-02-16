# Request/response validation happens in here
# schemas are the API contract. They define the structure of the data that the API expects to receive and send back.
# Models on the other hand are what define the Postgres database tables and structures.
# Think: Schemas are for the API layer & converting data from request/response bodies, Models are for the database layer. 

from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True