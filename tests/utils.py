from httpx import AsyncClient
from sqlalchemy import delete, select

from src.auth.models import User
from src.database import async_session_maker


async def get_all_users():
    async with async_session_maker() as session:
        statement = select(User)
        data = await session.execute(statement)
        return data.all()


async def get_user(email: str):
    async with async_session_maker() as session:
        statement = select(User).where(User.email == email)
        data = await session.execute(statement)
        return data.all()


async def delete_all_users():
    async with async_session_maker() as session:
        statement = delete(User)
        await session.execute(statement)
        await session.commit()


async def delete_user(email: str):
    async with async_session_maker() as session:
        statement = delete(User).where(User.email == email)
        await session.execute(statement)
        await session.commit()


async def register(ac: AsyncClient, email: str, username: str, password: str):
    return await ac.post(
        "auth/register",
        json={
            "email": email,
            "password": password,
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
            "name": username,
        },
    )
