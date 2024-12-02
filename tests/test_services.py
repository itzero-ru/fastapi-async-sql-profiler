from pprint import pprint
from fastapi_async_sql_profiler.repository import RequestInfoRepository
from fastapi_async_sql_profiler.services import RequestInfoService
from .conftest import client, async_session_maker


async def test_get_request_info_by_id():
    url = '/items'
    response = client.get(url)
    assert response.status_code == 200, "Status code should be 200"
    id = 1
    async with async_session_maker() as session:
        service = RequestInfoService(RequestInfoRepository(session))
        request_query = await service.get_request_info_by_id(id)
        assert request_query.id == id


async def test_get_request_info_all():

    url = '/items'
    response = client.get(url)
    assert response.status_code == 200, "Status code should be 200"

    async with async_session_maker() as session:
        service = RequestInfoService(RequestInfoRepository(session))
        page = 1
        size = 1
        result = await service.get_request_info_all(page=page, size=size)
        count = result.__len__()
        assert count > 0, "Count should be greater than 0"
