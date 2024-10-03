from sqlalchemy import insert, select, update, delete
from fastapi_async_sql_profiler.database import async_session_maker


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


async def get_obj_by_id(model, id: int) -> int:
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
