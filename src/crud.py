from sqlalchemy import insert, select, update, delete
from src.database import async_session_maker


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
