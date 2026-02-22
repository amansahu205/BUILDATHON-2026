from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

# Convert postgresql:// → postgresql+asyncpg:// and strip pgbouncer params
_raw_url = settings.DATABASE_URL.replace(
    "postgresql://", "postgresql+asyncpg://"
).replace(
    "postgres://", "postgresql+asyncpg://"
).split("?")[0]  # strip ?pgbouncer=true etc.

DATABASE_URL = _raw_url

engine = create_async_engine(
    DATABASE_URL,
    echo=settings.NODE_ENV == "development",
    connect_args={
        "statement_cache_size": 0,  # required for PgBouncer/Supabase pooler
        "ssl": "require",
        "server_settings": {"search_path": "public"},
    },
)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
