from typing import Annotated

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)

from backend.app.core.configuration import settings


async_engine: AsyncEngine | None = None
async_session_maker: async_sessionmaker[AsyncSession] | None = None


async def init_db():
    global async_engine, async_session_maker

    if async_engine:
        print("Database already initialized")
        return

    async_engine = create_async_engine(settings.DB_URI)

    async_session_maker = async_sessionmaker(
        async_engine,
        expire_on_commit=False,
    )


async def destroy_db():
    global async_engine

    if async_engine:
        await async_engine.dispose()
        async_engine = None


async def get_postgres_session():
    if not async_session_maker:
        raise RuntimeError("Database not initialized")

    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def postgres_session_provider(
        session: Annotated[AsyncSession, Depends(get_postgres_session)]
):
    return session
