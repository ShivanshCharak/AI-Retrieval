from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://shivansh:shamsher54@localhost:5432/ai_retrieval"


engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    future=True,
)


async def get_db():
    """Async generator for database session dependency injection."""
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()
