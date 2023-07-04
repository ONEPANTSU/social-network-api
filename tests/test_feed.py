from httpx import AsyncClient

from src.database import async_session_maker
from src.feed.schemas import PostCreate, PostUpdate
from src.feed.utils import (
    create_post_json,
    delete_post_json,
    dislike_post_json,
    edit_post_json,
    get_likes_by_post_id_json,
    get_posts_by_user_id_json,
    like_post_json,
    remove_the_reaction_json,
    view_post_json,
)
from src.utils import STATUS, return_json
from tests.constants import EMAIL, EMAIL_2, PASSWD, PASSWD_2, USERNAME, USERNAME_2
from tests.utils import delete_user, get_user, register


async def test_create_post(ac: AsyncClient):
    if len(await get_user(EMAIL)) == 0:
        response = await register(
            ac=ac, email=EMAIL, username=USERNAME, password=PASSWD
        )
        assert response.status_code == 201
    assert len(await get_user(EMAIL)) == 1

    user = await get_user(email=EMAIL)
    user_id = user[0][0].id

    post_to_create = PostCreate(title="Тестовый пост", text="Текст для тестового поста")

    right_response = return_json(
        status=STATUS[200],
        message=f"Пользователь #{user_id} успешно опубликовал пост",
    )
    async with async_session_maker() as session:
        response = await create_post_json(
            post_to_create=post_to_create, user_id=user_id, session=session
        )
    for key, value in right_response.items():
        assert value == response[key] or value is response[key]


async def test_right_edit_post(ac: AsyncClient):
    user = await get_user(email=EMAIL)
    user_id = user[0][0].id

    async with async_session_maker() as session:
        posts = await get_posts_by_user_id_json(user_id=user_id, session=session)
    post_id = posts["data"][-1]["id"]

    assert isinstance(post_id, int)

    post_update = PostUpdate(id=post_id, title="Новый загаловок", text="Новый текст")

    right_response = return_json(
        status=STATUS[200],
        message=f"Пост #{post_id} успешно изменён пользователем #{user_id}",
    )

    async with async_session_maker() as session:
        response = await edit_post_json(
            post_update=post_update, user_id=user_id, session=session
        )

    for key, value in right_response.items():
        assert value == response[key] or value is response[key]


async def test_edit_post_with_wrong_user(ac: AsyncClient):
    user = await get_user(email=EMAIL)
    user_id = user[0][0].id

    async with async_session_maker() as session:
        posts = await get_posts_by_user_id_json(user_id=user_id, session=session)
    post_id = posts["data"][-1]["id"]

    assert isinstance(post_id, int)

    post_update = PostUpdate(id=post_id, title="Новый загаловок", text="Новый текст")

    if len(await get_user(EMAIL_2)) == 0:
        response = await register(
            ac=ac, email=EMAIL_2, username=USERNAME_2, password=PASSWD_2
        )
        assert response.status_code == 201
    assert len(await get_user(EMAIL_2)) == 1
    wrong_user = await get_user(email=EMAIL_2)
    wrong_user_id = wrong_user[0][0].id

    right_response = return_json(
        status=STATUS[400],
        message=f"Пользователь #{wrong_user_id} не имеет права изменять пост #{post_id}",
    )

    async with async_session_maker() as session:
        response = await edit_post_json(
            post_update=post_update, user_id=wrong_user_id, session=session
        )

    for key, value in right_response.items():
        assert value == response[key] or value is response[key]


async def test_edit_post_with_wrong_post(ac: AsyncClient):
    user = await get_user(email=EMAIL)
    user_id = user[0][0].id

    async with async_session_maker() as session:
        posts = await get_posts_by_user_id_json(user_id=user_id, session=session)
    post_id = posts["data"][-1]["id"]

    assert isinstance(post_id, int)

    wrong_post_id = post_id + 1

    post_update = PostUpdate(
        id=wrong_post_id, title="Новый загаловок", text="Новый текст"
    )

    right_response = return_json(
        status=STATUS[400],
        message=f"Пост #{wrong_post_id} не существует",
    )

    async with async_session_maker() as session:
        response = await edit_post_json(
            post_update=post_update, user_id=user_id, session=session
        )

    for key, value in right_response.items():
        assert value == response[key] or value is response[key]


async def test_view_post():
    user = await get_user(email=EMAIL)
    user_id = user[0][0].id

    async with async_session_maker() as session:
        posts = await get_posts_by_user_id_json(user_id=user_id, session=session)
    post_id = posts["data"][-1]["id"]

    right_response = return_json(
        status=STATUS[200],
        message=f"Пост #{post_id} успешно просмотрем пользователем #{user_id}",
    )

    async with async_session_maker() as session:
        response = await view_post_json(
            post_id=post_id, user_id=user_id, session=session
        )

    for key, value in right_response.items():
        assert value == response[key] or value is response[key]


async def test_view_post_with_wrong_post():
    user = await get_user(email=EMAIL)
    user_id = user[0][0].id

    async with async_session_maker() as session:
        posts = await get_posts_by_user_id_json(user_id=user_id, session=session)
    wrong_post_id = posts["data"][-1]["id"] + 1

    right_response = return_json(
        status=STATUS[400],
        message=f"Пост #{wrong_post_id} не существует",
    )

    async with async_session_maker() as session:
        response = await view_post_json(
            post_id=wrong_post_id, user_id=user_id, session=session
        )

    for key, value in right_response.items():
        assert value == response[key] or value is response[key]


async def test_like_post_by_author(ac: AsyncClient):
    auth = await get_user(email=EMAIL)
    auth_id = auth[0][0].id

    async with async_session_maker() as session:
        posts = await get_posts_by_user_id_json(user_id=auth_id, session=session)
    post_id = posts["data"][-1]["id"]

    right_response = return_json(
        status=STATUS[400],
        message=f"Пользователь #{auth_id} попытался поставить реакцию на свой пост #{post_id} ",
    )

    async with async_session_maker() as session:
        response = await like_post_json(
            post_id=post_id, user_id=auth_id, session=session
        )

    for key, value in right_response.items():
        assert value == response[key] or value is response[key]


async def test_like_post(ac: AsyncClient):
    if len(await get_user(EMAIL_2)) == 0:
        response = await register(
            ac=ac, email=EMAIL_2, username=USERNAME_2, password=PASSWD_2
        )
        assert response.status_code == 201
    assert len(await get_user(EMAIL_2)) == 1
    user = await get_user(email=EMAIL_2)
    user_id = user[0][0].id

    auth = await get_user(email=EMAIL)
    auth_id = auth[0][0].id

    async with async_session_maker() as session:
        posts = await get_posts_by_user_id_json(user_id=auth_id, session=session)
    post_id = posts["data"][-1]["id"]

    right_response = return_json(
        status=STATUS[200],
        message=f"Пользователь #{user_id} успешно поставил лайк на пост #{post_id}",
    )

    async with async_session_maker() as session:
        await remove_the_reaction_json(
            post_id=post_id, user_id=user_id, session=session
        )
        response = await like_post_json(
            post_id=post_id, user_id=user_id, session=session
        )

    for key, value in right_response.items():
        assert value == response[key] or value is response[key]

    right_get_likes_data = {
        "total_reactions": 1,
        "likes": 1,
        "dislikes": 0,
    }
    async with async_session_maker() as session:
        get_likes_json = await get_likes_by_post_id_json(
            post_id=post_id, session=session
        )
        get_likes_data = get_likes_json["data"][0]

    for key, value in right_get_likes_data.items():
        assert value == get_likes_data[key] or value is get_likes_data[key]


async def test_double_like_post(ac: AsyncClient):
    if len(await get_user(EMAIL_2)) == 0:
        response = await register(
            ac=ac, email=EMAIL_2, username=USERNAME_2, password=PASSWD_2
        )
        assert response.status_code == 201
    assert len(await get_user(EMAIL_2)) == 1
    user = await get_user(email=EMAIL_2)
    user_id = user[0][0].id

    auth = await get_user(email=EMAIL)
    auth_id = auth[0][0].id

    async with async_session_maker() as session:
        posts = await get_posts_by_user_id_json(user_id=auth_id, session=session)
    post_id = posts["data"][-1]["id"]

    right_response = return_json(
        status=STATUS[200],
        message=f"Пользователь #{user_id} уже ставил лайк на пост #{post_id}",
    )

    async with async_session_maker() as session:
        await like_post_json(post_id=post_id, user_id=user_id, session=session)
        response = await like_post_json(
            post_id=post_id, user_id=user_id, session=session
        )

    for key, value in right_response.items():
        assert value == response[key] or value is response[key]

    right_get_likes_data = {
        "total_reactions": 1,
        "likes": 1,
        "dislikes": 0,
    }
    async with async_session_maker() as session:
        get_likes_json = await get_likes_by_post_id_json(
            post_id=post_id, session=session
        )
        get_likes_data = get_likes_json["data"][0]

    for key, value in right_get_likes_data.items():
        assert value == get_likes_data[key] or value is get_likes_data[key]


async def test_change_dislike_to_like_post(ac: AsyncClient):
    if len(await get_user(EMAIL_2)) == 0:
        response = await register(
            ac=ac, email=EMAIL_2, username=USERNAME_2, password=PASSWD_2
        )
        assert response.status_code == 201
    assert len(await get_user(EMAIL_2)) == 1
    user = await get_user(email=EMAIL_2)
    user_id = user[0][0].id

    auth = await get_user(email=EMAIL)
    auth_id = auth[0][0].id

    async with async_session_maker() as session:
        posts = await get_posts_by_user_id_json(user_id=auth_id, session=session)
    post_id = posts["data"][-1]["id"]

    right_response = return_json(
        status=STATUS[200],
        message=f"Пользователь #{user_id} убрал дизлайк и поставил лайк на пост #{post_id}",
    )

    async with async_session_maker() as session:
        await dislike_post_json(post_id=post_id, user_id=user_id, session=session)
        response = await like_post_json(
            post_id=post_id, user_id=user_id, session=session
        )

    for key, value in right_response.items():
        assert value == response[key] or value is response[key]

    right_get_likes_data = {
        "total_reactions": 1,
        "likes": 1,
        "dislikes": 0,
    }
    async with async_session_maker() as session:
        get_likes_json = await get_likes_by_post_id_json(
            post_id=post_id, session=session
        )
        get_likes_data = get_likes_json["data"][0]

    for key, value in right_get_likes_data.items():
        assert value == get_likes_data[key] or value is get_likes_data[key]


async def test_dislike_post_by_author(ac: AsyncClient):
    auth = await get_user(email=EMAIL)
    auth_id = auth[0][0].id

    async with async_session_maker() as session:
        posts = await get_posts_by_user_id_json(user_id=auth_id, session=session)
    post_id = posts["data"][-1]["id"]

    right_response = return_json(
        status=STATUS[400],
        message=f"Пользователь #{auth_id} попытался поставить реакцию на свой пост #{post_id} ",
    )

    async with async_session_maker() as session:
        response = await dislike_post_json(
            post_id=post_id, user_id=auth_id, session=session
        )

    for key, value in right_response.items():
        assert value == response[key] or value is response[key]


async def test_dislike_post(ac: AsyncClient):
    if len(await get_user(EMAIL_2)) == 0:
        response = await register(
            ac=ac, email=EMAIL_2, username=USERNAME_2, password=PASSWD_2
        )
        assert response.status_code == 201
    assert len(await get_user(EMAIL_2)) == 1
    user = await get_user(email=EMAIL_2)
    user_id = user[0][0].id

    auth = await get_user(email=EMAIL)
    auth_id = auth[0][0].id

    async with async_session_maker() as session:
        posts = await get_posts_by_user_id_json(user_id=auth_id, session=session)
    post_id = posts["data"][-1]["id"]

    right_response = return_json(
        status=STATUS[200],
        message=f"Пользователь #{user_id} успешно поставил дизлайк на пост #{post_id}",
    )

    async with async_session_maker() as session:
        await remove_the_reaction_json(
            post_id=post_id, user_id=user_id, session=session
        )
        response = await dislike_post_json(
            post_id=post_id, user_id=user_id, session=session
        )

    for key, value in right_response.items():
        assert value == response[key] or value is response[key]

    right_get_likes_data = {
        "total_reactions": 1,
        "likes": 0,
        "dislikes": 1,
    }
    async with async_session_maker() as session:
        get_likes_json = await get_likes_by_post_id_json(
            post_id=post_id, session=session
        )
        get_likes_data = get_likes_json["data"][0]

    for key, value in right_get_likes_data.items():
        assert value == get_likes_data[key] or value is get_likes_data[key]


async def test_double_dislike_post(ac: AsyncClient):
    if len(await get_user(EMAIL_2)) == 0:
        response = await register(
            ac=ac, email=EMAIL_2, username=USERNAME_2, password=PASSWD_2
        )
        assert response.status_code == 201
    assert len(await get_user(EMAIL_2)) == 1
    user = await get_user(email=EMAIL_2)
    user_id = user[0][0].id

    auth = await get_user(email=EMAIL)
    auth_id = auth[0][0].id

    async with async_session_maker() as session:
        posts = await get_posts_by_user_id_json(user_id=auth_id, session=session)
    post_id = posts["data"][-1]["id"]

    right_response = return_json(
        status=STATUS[200],
        message=f"Пользователь #{user_id} уже ставил дизлайк на пост #{post_id}",
    )

    async with async_session_maker() as session:
        await dislike_post_json(post_id=post_id, user_id=user_id, session=session)
        response = await dislike_post_json(
            post_id=post_id, user_id=user_id, session=session
        )

    for key, value in right_response.items():
        assert value == response[key] or value is response[key]

    right_get_likes_data = {
        "total_reactions": 1,
        "likes": 0,
        "dislikes": 1,
    }
    async with async_session_maker() as session:
        get_likes_json = await get_likes_by_post_id_json(
            post_id=post_id, session=session
        )
        get_likes_data = get_likes_json["data"][0]

    for key, value in right_get_likes_data.items():
        assert value == get_likes_data[key] or value is get_likes_data[key]


async def test_change_like_to_dislike_post(ac: AsyncClient):
    if len(await get_user(EMAIL_2)) == 0:
        response = await register(
            ac=ac, email=EMAIL_2, username=USERNAME_2, password=PASSWD_2
        )
        assert response.status_code == 201
    assert len(await get_user(EMAIL_2)) == 1
    user = await get_user(email=EMAIL_2)
    user_id = user[0][0].id

    auth = await get_user(email=EMAIL)
    auth_id = auth[0][0].id

    async with async_session_maker() as session:
        posts = await get_posts_by_user_id_json(user_id=auth_id, session=session)
    post_id = posts["data"][-1]["id"]

    right_response = return_json(
        status=STATUS[200],
        message=f"Пользователь #{user_id} убрал лайк и поставил дизлайк на пост #{post_id}",
    )

    async with async_session_maker() as session:
        await like_post_json(post_id=post_id, user_id=user_id, session=session)
        response = await dislike_post_json(
            post_id=post_id, user_id=user_id, session=session
        )

    for key, value in right_response.items():
        assert value == response[key] or value is response[key]

    right_get_likes_data = {
        "total_reactions": 1,
        "likes": 0,
        "dislikes": 1,
    }
    async with async_session_maker() as session:
        get_likes_json = await get_likes_by_post_id_json(
            post_id=post_id, session=session
        )
        get_likes_data = get_likes_json["data"][0]

    for key, value in right_get_likes_data.items():
        assert value == get_likes_data[key] or value is get_likes_data[key]


async def test_remove_the_reaction(ac: AsyncClient):
    if len(await get_user(EMAIL_2)) == 0:
        response = await register(
            ac=ac, email=EMAIL_2, username=USERNAME_2, password=PASSWD_2
        )
        assert response.status_code == 201
    assert len(await get_user(EMAIL_2)) == 1
    user = await get_user(email=EMAIL_2)
    user_id = user[0][0].id

    auth = await get_user(email=EMAIL)
    auth_id = auth[0][0].id

    async with async_session_maker() as session:
        posts = await get_posts_by_user_id_json(user_id=auth_id, session=session)
    post_id = posts["data"][-1]["id"]

    right_response = return_json(
        status=STATUS[200],
        message=f"Пользователь #{user_id} убрал реакцию на пост #{post_id}",
    )

    async with async_session_maker() as session:
        await like_post_json(post_id=post_id, user_id=user_id, session=session)
        response = await remove_the_reaction_json(
            post_id=post_id, user_id=user_id, session=session
        )

    for key, value in right_response.items():
        assert value == response[key] or value is response[key]

    async with async_session_maker() as session:
        await dislike_post_json(post_id=post_id, user_id=user_id, session=session)
        response = await remove_the_reaction_json(
            post_id=post_id, user_id=user_id, session=session
        )

    for key, value in right_response.items():
        assert value == response[key] or value is response[key]

    right_get_likes_data = {
        "total_reactions": 0,
        "likes": 0,
        "dislikes": 0,
    }
    async with async_session_maker() as session:
        get_likes_json = await get_likes_by_post_id_json(
            post_id=post_id, session=session
        )
        get_likes_data = get_likes_json["data"][0]

    for key, value in right_get_likes_data.items():
        assert value == get_likes_data[key] or value is get_likes_data[key]


async def test_double_remove_the_reaction(ac: AsyncClient):
    if len(await get_user(EMAIL_2)) == 0:
        response = await register(
            ac=ac, email=EMAIL_2, username=USERNAME_2, password=PASSWD_2
        )
        assert response.status_code == 201
    assert len(await get_user(EMAIL_2)) == 1
    user = await get_user(email=EMAIL_2)
    user_id = user[0][0].id

    auth = await get_user(email=EMAIL)
    auth_id = auth[0][0].id

    async with async_session_maker() as session:
        posts = await get_posts_by_user_id_json(user_id=auth_id, session=session)
    post_id = posts["data"][-1]["id"]

    right_response = return_json(
        status=STATUS[400],
        message=f"Пользователь #{user_id} ещё не ставил реакцию на пост #{post_id}",
    )

    async with async_session_maker() as session:
        await remove_the_reaction_json(
            post_id=post_id, user_id=user_id, session=session
        )
        response = await remove_the_reaction_json(
            post_id=post_id, user_id=user_id, session=session
        )

    for key, value in right_response.items():
        assert value == response[key] or value is response[key]

    right_get_likes_data = {
        "total_reactions": 0,
        "likes": 0,
        "dislikes": 0,
    }
    async with async_session_maker() as session:
        get_likes_json = await get_likes_by_post_id_json(
            post_id=post_id, session=session
        )
        get_likes_data = get_likes_json["data"][0]

    for key, value in right_get_likes_data.items():
        assert value == get_likes_data[key] or value is get_likes_data[key]


async def test_delete_post_with_wrong_user():
    user = await get_user(email=EMAIL)
    user_id = user[0][0].id

    async with async_session_maker() as session:
        posts = await get_posts_by_user_id_json(user_id=user_id, session=session)
    posts_data = posts["data"]

    wrong_user_id = user_id + 1

    for data in posts_data:
        post_id = data["id"]
        right_response = return_json(
            status=STATUS[400],
            message=f"Пользователь #{wrong_user_id} не имеет права удалять пост #{post_id}",
        )
        async with async_session_maker() as session:
            response = await delete_post_json(
                post_id=post_id, user_id=wrong_user_id, session=session
            )
        for key, value in right_response.items():
            assert value == response[key] or value is response[key]


async def test_delete_post_with_wrong_post():
    user = await get_user(email=EMAIL)
    user_id = user[0][0].id

    async with async_session_maker() as session:
        posts = await get_posts_by_user_id_json(user_id=user_id, session=session)
    wrong_post_id = posts["data"][-1]["id"] + 1

    right_response = return_json(
        status=STATUS[400],
        message=f"Пост #{wrong_post_id} не существует",
    )
    async with async_session_maker() as session:
        response = await delete_post_json(
            post_id=wrong_post_id, user_id=user_id, session=session
        )
    for key, value in right_response.items():
        assert value == response[key] or value is response[key]


async def test_delete_post():
    user = await get_user(email=EMAIL)
    user_id = user[0][0].id

    async with async_session_maker() as session:
        posts = await get_posts_by_user_id_json(user_id=user_id, session=session)
    posts_data = posts["data"]

    for data in posts_data:
        post_id = data["id"]
        right_response = return_json(
            status=STATUS[200],
            message=f"Пост #{post_id} успешно удален",
        )
        async with async_session_maker() as session:
            response = await delete_post_json(
                post_id=post_id, user_id=user_id, session=session
            )
        for key, value in right_response.items():
            assert value == response[key] or value is response[key]


async def test_delete_user():
    await delete_user(EMAIL)
    assert len(await get_user(EMAIL)) == 0
    await delete_user(EMAIL_2)
    assert len(await get_user(EMAIL_2)) == 0