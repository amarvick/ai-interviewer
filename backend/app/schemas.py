# Request/response validation happens in here
# schemas are the API contract. They define the structure of the data that the API expects to receive and send back.
# Models on the other hand are what define the Postgres database tables and structures.
# Think: Schemas are for the API layer & converting data from request/response bodies, Models are for the database layer. 

from pydantic import BaseModel

class ProblemCreate(BaseModel):
    title: str
    description: str
    difficulty: str
    category: str

class ProblemResponse(BaseModel):
    id: int
    title: str
    description: str
    difficulty: str
    category: str

    class Config:
        orm_mode = True

    