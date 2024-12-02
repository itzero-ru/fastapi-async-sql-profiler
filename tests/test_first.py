from pprint import pprint

from fastapi import Depends

from fastapi_async_sql_profiler.crud import filter_obj, get_obj_by_id
from fastapi_async_sql_profiler.models import Items, QueryInfo, RequestInfo
from fastapi_async_sql_profiler.repository import QueryInfoRepository, RequestInfoRepository, ResponseInfoRepository
from fastapi_async_sql_profiler.services import ItemService, RequestInfoService
from .conftest import client
import pytest
from fastapi_async_sql_profiler.database import async_session_maker


def test_requests_endpoint():

    url = '/profiler/requests'
    response = client.get(
        url,
        # json={'a': 1},
    )
    print(response)
    pprint(response.text)

    assert response.status_code == 200, "Status code should be 201"


def test_get_items():

    url = '/items'
    response = client.get(
        url,
        # json={'a': 1},
    )
    print(response)
    pprint(response.text)

    assert response.status_code == 200, "Status code should be 200"


async def test_post_items_profiler():

    post_body = {'body': 'first_item'}
    body_field_db = '{"body":"first_item"}'
    url = '/item'

    response = client.post(
        url,
        json=post_body,
    )
    assert response.status_code == 201, "Status code should be 201"

    # result = response.json()
    # item_id = result['id']

    async with async_session_maker() as session:
        item_requests = await RequestInfoRepository(session).list(filters={'body': body_field_db})

    request_item = item_requests[-1]
    response_id = request_item.response_info.id

    async with async_session_maker() as session:
        response_info = await ResponseInfoRepository(session).get_by_id(response_id)

    assert response_info.request_info_id == request_item.id

    async with async_session_maker() as session:
        queries = await QueryInfoRepository(session).list(request_id=request_item.id)

    assert request_item.total_queries == len(queries)


async def test_request_detail():

    url = '/items'
    response = client.get(url)

    async with async_session_maker() as session:
        request_info_list = await RequestInfoRepository(session).list()

    requests_info = request_info_list[-1]
    requests_info_id = requests_info.id

    url = f'/profiler/requests/{requests_info_id}'
    response = client.get(url)

    # print(response)
    # pprint(response.text)

    assert response.status_code == 200, "Status code should be 200"


@pytest.mark.asyncio
async def test_sql_parse():

    url = '/items'
    response = client.get(url)
    assert response.status_code == 200, "Status code should be 200"

    async with async_session_maker() as session:
        request_info_list = await RequestInfoRepository(session).list()

    requests_info = request_info_list[-1]
    requests_info_id = requests_info.id

    id = requests_info_id

    queries = await filter_obj(QueryInfo, request_id=id)
    print(queries)
    q = queries[0]

    assert q.num_joins == 0
    assert q.tables_involved == ['fasp_items']
    assert q.get_tables_from_query == ['fasp_items']
    assert q.formatted_query == "SELECT fasp_items.id,\n       fasp_items.body\nFROM fasp_items\nWHERE fasp_items.body = 'string'\nORDER BY fasp_items.id DESC"
