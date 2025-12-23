import asyncpg
import logging
from src.config import settings

class Database:
    def __init__(self):
        self.pool: asyncpg.Pool | None = None

    async def connect(self):
        """Создает пул подключений к БД."""
        if not self.pool:
            try:
                self.pool = await asyncpg.create_pool(
                    user=settings.POSTGRES_USER,
                    password=settings.POSTGRES_PASSWORD,
                    database=settings.POSTGRES_DB,
                    host=settings.POSTGRES_HOST,
                    port=settings.POSTGRES_PORT,
                    min_size=1,
                    max_size=20 # Настраиваем под нагрузку
                )
                logging.info("Успешное подключение к PostgreSQL")
            except Exception as e:
                logging.error(f"Ошибка подключения к БД: {e}")
                raise e

    async def disconnect(self):
        """Закрывает пул подключений."""
        if self.pool:
            await self.pool.close()
            logging.info("Отключение от PostgreSQL")

    async def fetchval(self, query: str, *args):
        """Выполняет запрос и возвращает одно значение (для ответов бота)."""
        if not self.pool:
            await self.connect()
        
        async with self.pool.acquire() as connection:
            return await connection.fetchval(query, *args)

    async def execute(self, query: str, *args):
        """Выполняет запрос без возврата данных (INSERT, UPDATE)."""
        if not self.pool:
            await self.connect()

        async with self.pool.acquire() as connection:
            return await connection.execute(query, *args)
    
    async def get_pool(self):
        if not self.pool:
            await self.connect()
        return self.pool

# Глобальный объект БД
db = Database()
