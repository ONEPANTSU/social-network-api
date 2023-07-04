from httpx import AsyncClient

from tests.constants import EMAIL, PASSWD, USERNAME
from tests.utils import delete_all_users, delete_user, get_user, register

# from tests.conftest import async_session_maker

# async def test_delete_all_users():
#     await delete_all_users()
#     assert len(await get_all_users()) == 0


async def test_register(ac: AsyncClient):
    # await delete_all_users()
    assert len(await get_user(EMAIL)) == 0
    response = await register(ac=ac, email=EMAIL, username=USERNAME, password=PASSWD)
    assert response.status_code == 201
    assert len(await get_user(EMAIL)) == 1


async def test_delete_user():
    await delete_user(EMAIL)
    assert len(await get_user(EMAIL)) == 0
