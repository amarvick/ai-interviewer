# Request/response validation happens in here
# schemas are the API contract. They define the structure of the data that the API expects to receive and send back.
# Models on the other hand are what define the Postgres database tables and structures.
# Think: Schemas are for the API layer & converting data from request/response bodies, Models are for the database layer. 

from pydantic import BaseModel, Field
from app.schemas.testcase import TestCasePublicResponse

class ProblemCreate(BaseModel):
    id: str | None = None
    title: str
    description: str
    difficulty: str
    category: str
    starter_code: dict[str, str] | None = None

class ProblemResponse(BaseModel):
    id: str
    title: str
    description: str
    difficulty: str
    category: str
    starter_code: dict[str, str]
    test_cases: list[TestCasePublicResponse] = Field(default_factory=list)

    class Config:
        orm_mode = True

class ProblemListCreate(BaseModel):
    name: str
    icon_url: str

class ProblemListResponse(BaseModel):
    id: str
    name: str
    icon_url: str

    class Config:
        orm_mode = True


class ProblemListProblemsResponse(BaseModel):
    name: str
    problems: list[ProblemResponse]
