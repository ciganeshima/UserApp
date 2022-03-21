from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserUpdate(BaseModel):
    username: str
    email: str


class ShowUser(BaseModel):
    username: str
    email: str
    is_active: bool

    class Config():  # tells pydantic to convert even non dict obj to json
        orm_mode = True
