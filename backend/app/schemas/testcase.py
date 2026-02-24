from typing import Any
from pydantic import BaseModel

class TestCasePublicResponse(BaseModel):
    id: int
    params: Any
    expected_output: Any

    class Config:
        orm_mode = True
