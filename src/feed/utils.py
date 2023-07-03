from typing import Optional

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.feed.models import Post, post
from src.feed.schemas import PostCreate, PostRead, PostUpdate
from src.utils import STATUS, logger, return_json


@logger.catch
async def get_post_by_id(post_id: int, session: AsyncSession) -> Optional[Post]:
    try:
        posts = await session.execute(select(post).filter_by(id=post_id))
        row = posts.one()
        gotten_post = Post(
            id=row.id,
            title=row.title,
            text=row.text,
            views=row.views,
            user_id=row.user_id,
        )
        return gotten_post
    except Exception as e:
        logger.error(str(e))
        return None


@logger.catch
def create_dict_from_post_data(post_data: Post) -> dict:
    return {
        "id": post_data.id,
        "title": post_data.title,
        "text": post_data.text,
        "views": post_data.views,
        "user_id": post_data.user_id,
    }


@logger.catch
async def get_post_by_post_id_json(post_id: int, session: AsyncSession):
    try:
        post_data = await get_post_by_id(post_id=post_id, session=session)
        if post_data is not None:
            data = [create_dict_from_post_data(post_data=post_data)]
            return return_json(status=STATUS[200], data=data)
        else:
            return return_json(status=STATUS[400], message=f"Пост #{post_id} не найден")
    except Exception as e:
        logger.error(e)
        return return_json(
            status=STATUS[400],
            message=f"Произошла ошибка при получении поста #{post_id}",
            details=str(e),
        )


@logger.catch
async def get_posts_by_user_id_json(user_id: int, session: AsyncSession) -> dict:
    try:
        posts = await session.execute(select(post).filter_by(user_id=user_id))
        data = posts.all()
        post_read_data = []

        for row in data:
            post_read_data.append(
                PostRead(
                    id=row.id,
                    title=row.title,
                    text=row.text,
                    views=row.views,
                    user_id=row.user_id,
                ).dict()
            )

        return return_json(status=STATUS[200], data=post_read_data)
    except Exception as e:
        logger.error(str(e))
        return return_json(
            status=STATUS[400],
            message=f"Произошла ошибка при получении постов пользователя #{user_id}",
            details=str(e),
        )


@logger.catch
async def create_post_json(
    post_to_create: PostCreate, user: User, session: AsyncSession
) -> dict:
    try:
        new_post = Post(
            title=post_to_create.title, text=post_to_create.text, user_id=user.id
        )
        session.add(new_post)
        await session.commit()
        return return_json(
            status=STATUS[200],
            message=f"Пользователь #{user.id} успешно опубликовал пост",
        )
    except Exception as e:
        logger.error(str(e))
        return return_json(
            status=STATUS[400],
            message=f"Произошла ошибка при публикации поста пользователем #{user.id}",
            details=str(e),
        )


@logger.catch
async def delete_post_json(post_id: int, user: User, session: AsyncSession) -> dict:
    try:
        gotten_post = await get_post_by_id(post_id=post_id, session=session)
        if gotten_post is not None:
            if gotten_post.user_id == user.id:
                statement = delete(Post).where(Post.id == post_id)
                await session.execute(statement)
                await session.commit()
                return return_json(
                    status=STATUS[200],
                    message=f"Пост #{post_id} успешно удален",
                )
            else:
                return return_json(
                    status=STATUS[400],
                    message=f"Пользователь #{user.id} не имеет права удалять пост #{post_id}",
                )
        else:
            return return_json(
                status=STATUS[400],
                message=f"Пост #{post_id} не существует",
            )
    except Exception as e:
        logger.error(str(e))
        return return_json(
            status=STATUS[400],
            message=f"Произошла ошибка при удалении поста #{post_id} пользователем #{user.id}",
            details=str(e),
        )


@logger.catch
async def edit_post_json(
    post_update: PostUpdate,
    user: User,
    session: AsyncSession,
) -> dict:
    try:
        post_id = post_update.id
        gotten_post = await get_post_by_id(post_id=post_id, session=session)
        if gotten_post is not None:
            if gotten_post.user_id == user.id:
                statement = (
                    update(Post)
                    .where(Post.id == post_id)
                    .values(title=post_update.title, text=post_update.text)
                )
                await session.execute(statement)
                await session.commit()
                return return_json(
                    status=STATUS[200],
                    message=f"Пост #{post_id} успешно изменён",
                )
            else:
                return return_json(
                    status=STATUS[400],
                    message=f"Пользователь #{user.id} не имеет права изменять пост #{post_id}",
                )
        else:
            return return_json(
                status=STATUS[400],
                message=f"Пост #{post_id} не существует",
            )
    except Exception as e:
        logger.error(str(e))
        return return_json(
            status=STATUS[400],
            message=f"Произошла ошибка при изменении поста #{post_update.id} пользователем #{user.id}",
            details=str(e),
        )


@logger.catch
async def view_post_json(
    post_id: int,
    user: User,
    session: AsyncSession,
) -> dict:
    try:
        gotten_post = await get_post_by_id(post_id=post_id, session=session)
        if gotten_post is not None:
            statement = (
                update(Post)
                .where(Post.id == post_id)
                .values(views=gotten_post.views + 1)
            )
            await session.execute(statement)
            await session.commit()
            return return_json(
                status=STATUS[200],
                message=f"Пост #{post_id} успешно просмотрем пользователем #{user.id}",
            )

        else:
            return return_json(
                status=STATUS[400],
                message=f"Пост #{post_id} не существует",
            )
    except Exception as e:
        logger.error(str(e))
        return return_json(
            status=STATUS[400],
            message=f"Произошла ошибка при просмотре поста #{post_id} пользователем #{user.id}",
            details=str(e),
        )
