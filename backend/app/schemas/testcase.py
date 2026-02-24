from typing import Any
from pydantic import BaseModel


class TestCaseCreate(BaseModel):
    problem_id: str
    params: Any
    expected_output: Any
    is_hidden: bool = False


class TestCaseResponse(BaseModel):
    id: int
    problem_id: str
    params: Any
    expected_output: Any
    is_hidden: bool

    class Config:
        orm_mode = True


class TestCasePublicResponse(BaseModel):
    id: int
    params: Any
    expected_output: Any

    class Config:
        orm_mode = True
