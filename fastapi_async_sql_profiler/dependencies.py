from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_async_sql_profiler.database import get_async_session
from fastapi_async_sql_profiler.repository import QueryInfoRepository, RequestInfoRepository
from fastapi_async_sql_profiler.services import QueryInfoService, RequestInfoService


async def get_request_info_repository(
    db: AsyncSession = Depends(get_async_session)
):
    return RequestInfoRepository(db)


async def get_request_info_service(
    repo: RequestInfoRepository = Depends(get_request_info_repository)
):
    return RequestInfoService(repo)


# query

async def get_query_info_repository(
    db: AsyncSession = Depends(get_async_session)
):
    return QueryInfoRepository(db)


async def get_query_info_service(
    repo: QueryInfoRepository = Depends(get_query_info_repository)
):
    return QueryInfoService(repo)