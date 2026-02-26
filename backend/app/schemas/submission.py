# Request/response validation happens in here
# schemas are the API contract. They define the structure of the data that the API expects to receive and send back.
# Models on the other hand are what define the Postgres database tables and structures.
# Think: Schemas are for the API layer & converting data from request/response bodies, Models are for the database layer. 

from datetime import datetime
from pydantic import BaseModel
from app.core.constants import Language, SubmissionResult

class SubmissionSubmit(BaseModel):
    problem_id: str
    code_submitted: str
    language: Language

class SubmissionResponse(BaseModel):
    id: str
    user_id: str
    problem_id: str
    code_submitted: str
    language: Language
    result: SubmissionResult
    error: str | None = None
    created_at: datetime

    class Config:
        orm_mode = True
