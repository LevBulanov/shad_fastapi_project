from pydantic import BaseModel

__all__ = [
    "CreateToken",
    "ReturnToken",
]

class CreateToken(BaseModel):
    email: str
    password: str

class ReturnToken(BaseModel):
    access_token: str
    token_type: str = "bearer"