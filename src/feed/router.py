from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.base_config import current_user
from src.auth.models import User
from src.database import get_async_session
from src.feed.schemas import PostCreate, PostUpdate
from src.feed.utils import (
    create_post_json,
    delete_post_json,
    dislike_post_json,
    edit_post_json,
    get_likes_by_post_id_json,
    get_post_by_post_id_json,
    get_posts_by_user_id_json,
    like_post_json,
    remove_the_reaction_json,
    view_post_json,
)

router = APIRouter()


@router.get("/get_post/{post_id}")
async def get_post_by_post_id(
    post_id: int, session: AsyncSession = Depends(get_async_session)
) -> dict:
    return await get_post_by_post_id_json(post_id=post_id, session=session)


@router.get("/get_reactions/{post_id}")
async def get_reactions_by_post_id(
    post_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    return await get_likes_by_post_id_json(post_id=post_id, session=session)


@router.get("/get_posts/{user_id}")
async def get_posts_by_user_id(
    user_id: int, session: AsyncSession = Depends(get_async_session)
) -> dict:
    return await get_posts_by_user_id_json(user_id=user_id, session=session)


@router.post("/create_post")
async def create_post(
    post_to_create: PostCreate,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    return await create_post_json(
        post_to_create=post_to_create, user_id=user.id, session=session
    )


@router.delete("/delete_post/{post_id}")
async def delete_post(
    post_id: int,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    return await delete_post_json(post_id=post_id, user_id=user.id, session=session)


@router.put("/edit_post/{post_id}")
async def edit_post(
    post_update: PostUpdate,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    return await edit_post_json(
        post_update=post_update, user_id=user.id, session=session
    )


@router.put("/view_post/{post_id}")
async def view_post(
    post_id: int,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    return await view_post_json(post_id=post_id, user_id=user.id, session=session)


@router.put("/like_post/{post_id}")
async def like_post(
    post_id: int,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    return await like_post_json(post_id=post_id, user_id=user.id, session=session)


@router.put("/dislike_post/{post_id}")
async def dislike_post(
    post_id: int,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    return await dislike_post_json(post_id=post_id, user_id=user.id, session=session)


@router.delete("/remove_the_reaction/{post_id}")
async def remove_the_reaction(
    post_id: int,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    return await remove_the_reaction_json(
        post_id=post_id, user_id=user.id, session=session
    )
