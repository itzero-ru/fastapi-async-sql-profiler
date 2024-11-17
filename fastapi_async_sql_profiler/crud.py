from typing import Sequence
from sqlalchemy import desc, insert, select, update, delete
from fastapi_async_sql_profiler.database import Base, async_session_maker
from sqlalchemy import func
from sqlalchemy.orm import aliased
from sqlalchemy.orm import joinedload, load_only
from sqlalchemy.exc import SQLAlchemyError
from fastapi_async_sql_profiler.models import QueryInfo, RequestInfo


async def add_one(model, data: dict) -> int:
    async with async_session_maker() as session:
        stmt = insert(model).values(**data).returning(model.id)
        res = await session.execute(stmt)
        await session.commit()

        return res.scalar_one()


async def add_db(model: Base) -> Base:
    try:
        async with async_session_maker() as session:
            session.add(model)
            await session.flush()
            await session.commit()
            return model
    except SQLAlchemyError as e:
        # Log the error or handle it as appropriate for your application
        print(f"An error occurred: {e}")
        raise SQLAlchemyError(e)


async def get_obj_by_id(
    model, id: int,
    joinedload_names: list | None = None,
) -> RequestInfo:
    async with async_session_maker() as session:
        # obj = await session.get(model, id)
        stmt = select(model).where(model.id == id)

        # joinedload
        if joinedload_names:
            for name in joinedload_names:
                if isinstance(name, str):
                    # String attribute name
                    attr = getattr(model, name, None)
                    if attr is not None:
                        stmt = stmt.options(joinedload(attr))
                else:
                    # Attribute model obj
                    stmt = stmt.options(joinedload(name))

        obj = await session.execute(stmt)
        # obj = obj.scalar_one()
        obj = obj.scalar_one_or_none()

        return obj


async def filter_obj(
    model,
    joinedload_names: list | None = None,
    exclude_fields: list | None = None,
    # joinedload_names: list = ['response_info', ],
    **kwargs,
) -> list:
    async with async_session_maker() as session:
        # stmt = select(model).where(model.id == kwargs['id'])

        all_fields = set(column.key for column in model.__table__.columns)
        if exclude_fields:
            fields_to_load: set = all_fields - set(exclude_fields)
            model_fields_to_load: list = [getattr(model, f) for f in fields_to_load]
            stmt = select(model).options(load_only(*model_fields_to_load))
        else:
            stmt = select(model)
        # stmt = select(model)

        # joinedload
        if joinedload_names:
            for name in joinedload_names:
                if isinstance(name, str):
                    attr = getattr(model, name, None)
                    if attr is not None:
                        stmt = stmt.options(joinedload(attr))
                else:
                    stmt = stmt.options(joinedload(name))

        # stmt = stmt.options(joinedload(*joinedload_names))
        # stmt = stmt.options(joinedload(RequestInfo.response_info))
        stmt = stmt.filter_by(**kwargs)
        stmt = stmt.order_by(desc(model.id))
        res = await session.execute(stmt)

        return res.scalars().all()
    # def filter(self, **kwargs):
    #     query = self.session.query(Offer)
    #     return query.filter_by(**kwargs).all()



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
