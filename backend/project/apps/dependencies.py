from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from project.core.settings import async_session


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        async with session.begin():
            yield session
