from pprint import pprint

from fastapi_async_sql_profiler.crud import filter_obj, get_obj_by_id
from fastapi_async_sql_profiler.models import QueryInfo, RequestInfo
from .conftest import client
import pytest


def test_first():

    assert 1 == 1


def test_two():

    assert 1 == 1
    url = '/profiler/111'
    response = client.post(
        url,
        # json={'a': 1},
    )

    # print(response.status_code)
    assert response.status_code == 200, "Status code should be 201"


def test_request_detail():

    url = '/profiler/request_detail/1'
    response = client.get(
        url,
        # json={'a': 1},
    )

    print(response)
    pprint(response.text)

    assert response.status_code == 200, "Status code should be 201"


@pytest.mark.asyncio
async def test_sql_parse():

    id = 3
    request_query = await get_obj_by_id(
        RequestInfo,
        id,
        joinedload_names=['response_info',]
    )
    print(request_query)
    print(request_query.id)

    queries = await filter_obj(QueryInfo, request_id=id)
    print(queries)
    q = queries[1]
    num_joins = q.num_joins
    tables_involved = q.tables_involved
    get_tables_from_query = q.get_tables_from_query
    formatted_query = q.formatted_query
    pprint(formatted_query)
    print('num_joins', num_joins)
    print('tables_involved', tables_involved)
    print('get_tables_from_query', get_tables_from_query)

    assert 1 == 1
