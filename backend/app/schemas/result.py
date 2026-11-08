from pydantic import BaseModel, Field

class StudentResultRequest(BaseModel):
    board: str = Field(min_length=2, max_length=30)
    exam: str = Field(min_length=2, max_length=50)
    year: int = Field(ge=1990, le=2100)

    result_type: int

    roll: str = Field(min_length=1, max_length=30)
    reg: str = Field(min_length=1, max_length=30)

    eiin: str | None = None
    dcode: str | None = None
    ccode: str | None = None

class StudentResultResponse(BaseModel):
    success: bool
    message: str
    data: dict | None = None