from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from settings.config import PostgresConfig


class Database:

    def __init__(self, config: PostgresConfig):
        self.engine = create_async_engine(url=str(config.dsn), echo=config.echo, pool_size=5, max_overflow=10)

        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=config.autoflush,
            autocommit=config.autocommit,
            expire_on_commit=config.expire_on_commit
        )

    @asynccontextmanager
    async def get_db_session(self):
        from sqlalchemy import exc

        session: AsyncSession = self.session_factory()
        try:
            yield session
        except exc.SQLAlchemyError:
            await session.rollback()
            raise
        finally:
            await session.close()
