from pprint import pprint
from fastapi_async_sql_profiler.repository import RequestInfoRepository
from fastapi_async_sql_profiler.services import RequestInfoService
from .conftest import client, async_session_maker


async def test_get_request_info_by_id():
    id = 1
    async with async_session_maker() as session:
        service = RequestInfoService(RequestInfoRepository(session))
        request_query = await service.get_request_info_by_id(id)
        pass
        print('@@@@@@@@@@@@')
        pprint(request_query)
        assert request_query.id == id