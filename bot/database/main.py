# todo: Database engine
from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = "sqlite+aiosqlite:///bot/database/DatabaseVPN.db"


def engine():
    return create_async_engine(DATABASE_URL)
