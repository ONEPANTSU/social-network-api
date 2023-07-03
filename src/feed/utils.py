from typing import Optional, List

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.feed.models import Post, post, user_post, UserPost
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


@logger.catch
async def get_user_post(user_id: int, post_id: int, session: AsyncSession) -> Optional[UserPost]:
    try:
        existing_user_post = await session.execute(select(user_post).filter_by(user_id=user_id, post_id=post_id))
        row = existing_user_post.one()
        gotten_user_post = UserPost(
            user_id=row.user_id,
            post_id=row.post_id,
            like=row.like,
        )
        return gotten_user_post
    except Exception as e:
        logger.error(str(e))
        return None


@logger.catch
async def like_post_json(
    post_id: int,
    user: User,
    session: AsyncSession,
) -> dict:
    try:
        existing_user_post = await get_user_post(user_id=user.id, post_id=post_id, session=session)
        if existing_user_post is None:
            new_user_post = UserPost(user_id=user.id, post_id=post_id, like=True)
            session.add(new_user_post)
            await session.commit()
            return return_json(
                status=STATUS[200],
                message=f"Пользователь #{user.id} успешно поставил лайк на пост #{post_id}",
            )
        elif existing_user_post.like:
            return return_json(
                status=STATUS[200],
                message=f"Пользователь #{user.id} уже ставил лайк на пост #{post_id}",
            )
        else:
            statement = (
                update(UserPost)
                .where(UserPost.user_id == user.id and UserPost.post_id == post_id)
                .values(like=True)
            )
            await session.execute(statement)
            await session.commit()
            return return_json(
                status=STATUS[200],
                message=f"Пользователь #{user.id} убрал дизлайк и поставил лайк на пост #{post_id}",
            )
    except Exception as e:
        logger.error(str(e))
        return return_json(
            status=STATUS[400],
            message=f"Произошла ошибка при попытке поставить лайк на пост #{post_id} пользователем #{user.id}",
            details=str(e),
        )


@logger.catch
async def dislike_post_json(
    post_id: int,
    user: User,
    session: AsyncSession,
) -> dict:
    try:
        existing_user_post = await get_user_post(user_id=user.id, post_id=post_id, session=session)
        if existing_user_post is None:
            new_user_post = UserPost(user_id=user.id, post_id=post_id, like=False)
            session.add(new_user_post)
            await session.commit()
            return return_json(
                status=STATUS[200],
                message=f"Пользователь #{user.id} успешно поставил дизлайк на пост #{post_id}",
            )
        elif not existing_user_post.like:
            return return_json(
                status=STATUS[200],
                message=f"Пользователь #{user.id} уже ставил дизлайк на пост #{post_id}",
            )
        else:
            statement = (
                update(UserPost)
                .where(UserPost.user_id == user.id and UserPost.post_id == post_id)
                .values(like=False)
            )
            await session.execute(statement)
            await session.commit()
            return return_json(
                status=STATUS[200],
                message=f"Пользователь #{user.id} убрал лайк и поставил дизлайк на пост #{post_id}",
            )
    except Exception as e:
        logger.error(str(e))
        return return_json(
            status=STATUS[400],
            message=f"Произошла ошибка при попытке поставить дизлайк на пост #{post_id} пользователем #{user.id}",
            details=str(e),
        )


@logger.catch
async def remove_the_reaction_json(
    post_id: int,
    user: User,
    session: AsyncSession,
) -> dict:
    try:
        existing_user_post = await get_user_post(user_id=user.id, post_id=post_id, session=session)
        if existing_user_post is None:
            return return_json(
                status=STATUS[400],
                message=f"Пользователь #{user.id} ещё не ставил реакцию на пост #{post_id}",
            )
        else:
            statement = (
                delete(UserPost)
                .where(UserPost.user_id == user.id and UserPost.post_id == post_id)
            )
            await session.execute(statement)
            await session.commit()
            return return_json(
                status=STATUS[200],
                message=f"Пользователь #{user.id} убрал реакцию на пост #{post_id}",
            )
    except Exception as e:
        logger.error(str(e))
        return return_json(
            status=STATUS[400],
            message=f"Произошла ошибка при попытке убрать реакцию на пост #{post_id} пользователем #{user.id}",
            details=str(e),
        )


@logger.catch
async def get_all_user_post_by_post_id(post_id: int, session: AsyncSession) -> Optional[List[UserPost]]:
    try:
        existing_user_post = await session.execute(select(user_post).filter_by(post_id=post_id))
        data = existing_user_post.all()
        gotten_user_post = []
        for row in data:
            gotten_user_post.append(UserPost(
                user_id=row.user_id,
                post_id=row.post_id,
                like=row.like,
            ))
        return gotten_user_post
    except Exception as e:
        logger.error(str(e))
        return None


@logger.catch
async def get_likes_by_post_id_json(
    post_id: int,
    session: AsyncSession,
) -> dict:
    try:
        gotten_post = await get_post_by_id(post_id=post_id, session=session)
        if gotten_post is not None:
            existing_user_post = await get_all_user_post_by_post_id(post_id=post_id, session=session)
            if existing_user_post is not None:
                likes_count = sum(1 for user_post_element in existing_user_post if user_post_element.like)
                dislikes_count = len(existing_user_post) - likes_count
                data = [{"total_reactions": len(existing_user_post), "likes": likes_count, "dislikes": dislikes_count}]
                return return_json(
                    status=STATUS[200],
                    message=f"Успешно получены реакции на пост #{post_id}",
                    data=data
                )
            else:
                return return_json(
                    status=STATUS[200],
                    message=f"На данный момент нет реакций на пост #{post_id}",
                )
        else:
            return return_json(
                status=STATUS[400],
                message=f"Пост #{post_id} не найден",
            )
    except Exception as e:
        logger.error(str(e))
        return return_json(
            status=STATUS[400],
            message=f"Произошла ошибка при попытке получить реакции на пост #{post_id}",
            details=str(e),
        )
