from pydantic import BaseModel

from .books import ReturnedBook


class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    email: str


class CreateSeller(BaseSeller):
    password: str


class ReadSeller(BaseSeller):
    id: int

class ReadSellerAndBooks(BaseSeller):
    id: int
    books: list[ReturnedBook]

class ReadAllSellers(BaseModel):
    sellers: list[ReadSeller]

class PatchSeller(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None

class UpdateSeller(BaseSeller):
    pass  

