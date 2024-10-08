from sqlalchemy import insert, select, update, delete
from fastapi_async_sql_profiler.database import async_session_maker
from sqlalchemy import func
from sqlalchemy.orm import aliased

from fastapi_async_sql_profiler.models import QueryInfo, RequestInfo


async def add_one(model, data: dict) -> int:
    async with async_session_maker() as session:
        stmt = insert(model).values(**data).returning(model.id)
        res = await session.execute(stmt)
        await session.commit()

        return res.scalar_one()


async def add_db(model) -> int:
    async with async_session_maker() as session:
        res = session.add(model)
        await session.commit()

        return res


async def get_obj_by_id(model, id: int) -> RequestInfo:
    async with async_session_maker() as session:
        obj = await session.get(model, id)

        return obj


async def filter_obj(model, **kwargs) -> list:
    async with async_session_maker() as session:
        # stmt = select(model).where(model.id == kwargs['id'])
        stmt = select(model).filter_by(**kwargs)
        res = await session.execute(stmt)

        return res.scalars().all()
    # def filter(self, **kwargs):
    #     query = self.session.query(Offer)
    #     return query.filter_by(**kwargs).all()


async def clear_table_bd(model):
    async with async_session_maker() as session:
        async with session.begin():
            query = delete(model)
            await session.execute(query)
        # bbb = await session.commit()
        # query = delete(model)
        # aaa = await session.execute(query)
        # res = await session.commit()

        return


async def get_requests_with_query_count():

    async with async_session_maker() as session:
        async with session.begin():
            # Создаем псевдоним для подзапроса
            query_count = aliased(QueryInfo)
            # Формируем запрос
            stmt = (
                select(
                    RequestInfo,
                    func.count(query_count.id).label('query_count')
                )
                .outerjoin(
                    query_count, RequestInfo.id == query_count.request_id)
                .group_by(RequestInfo.id)
            )
            # Выполняем запрос асинхронно
            result = await session.execute(stmt)

            # Возвращаем результат
            return result.scalars().all()

