from typing import Optional

from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    name: str


class UserCreate(schemas.BaseUserCreate):
    name: str


class UserUpdate(schemas.BaseUserUpdate):
    name: Optional[str]
