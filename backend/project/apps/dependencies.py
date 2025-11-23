from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from project.core.settings import async_session


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session with automatic transaction management."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
