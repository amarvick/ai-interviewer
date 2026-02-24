# Request/response validation happens in here
# schemas are the API contract. They define the structure of the data that the API expects to receive and send back.
# Models on the other hand are what define the Postgres database tables and structures.
# Think: Schemas are for the API layer & converting data from request/response bodies, Models are for the database layer. 

from pydantic import BaseModel
from app.core.constants import Language, SubmissionResult

class SubmissionSubmit(BaseModel):
    problem_id: str
    code_submitted: str
    language: Language

class SubmissionCreate(BaseModel):
    user_id: str
    problem_id: str
    code_submitted: str
    language: Language
    result: SubmissionResult

class SubmissionResponse(BaseModel):
    id: str
    user_id: str
    problem_id: str
    code_submitted: str
    language: Language
    result: SubmissionResult

    class Config:
        orm_mode = True
