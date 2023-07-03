from pydantic import BaseModel


class PostCreate(BaseModel):
    title: str
    text: str


class PostRead(BaseModel):
    id: int
    title: str
    text: str
    views: int
    user_id: int


class PostUpdate(BaseModel):
    id: int
    title: str
    text: str
