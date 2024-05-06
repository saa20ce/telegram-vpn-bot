from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.main import engine
from bot.database.models.main import Servers, StaticPersons, PromoCode


async def delete_server(name):
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        statement = select(Servers).filter(Servers.name == name)
        result = await db.execute(statement)
        server = result.scalar_one_or_none()

        if server is not None:
            await db.delete(server)
            await db.commit()
        else:
            raise ModuleNotFoundError


async def delete_static_user_bd(name):
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        statement = select(StaticPersons).filter(StaticPersons.name == name)
        result = await db.execute(statement)
        static_user = result.scalar_one_or_none()

        if static_user is not None:
            await db.delete(static_user)
            await db.commit()
        else:
            raise ModuleNotFoundError


async def delete_promo_code(id_promo):
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        statement = select(PromoCode).filter(PromoCode.id == id_promo)
        result = await db.execute(statement)
        promo_code = result.scalar_one_or_none()

        if promo_code is not None:
            await db.delete(promo_code)
            await db.commit()
        else:
            raise ModuleNotFoundError
