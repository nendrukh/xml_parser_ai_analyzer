from config import POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_PORT, POSTGRES_USER, POSTGRES_HOST

import asyncpg


class Database:
    @staticmethod
    async def _connect_to_db():
        return await asyncpg.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            database=POSTGRES_DB,
            password=POSTGRES_PASSWORD
        )

    @classmethod
    async def execute_to_db(cls, query: str, *params):
        try:
            conn = await cls._connect_to_db()
            await conn.execute(query, *params)
        finally:
            await conn.close()

    @classmethod
    async def fetch_to_db(cls, query: str, *params):
        try:
            conn = await cls._connect_to_db()
            response = await conn.fetch(query, *params)
        finally:
            await conn.close()

        return response

    @classmethod
    async def create_tables(cls):
        try:
            conn = await cls._connect_to_db()
            await conn.execute("""CREATE TABLE IF NOT EXISTS ai_analytics (
            id SERIAL PRIMARY KEY,
            sales_date DATE,
            prompt TEXT,
            ai_answer TEXT,
            status VARCHAR(32)
            );
            CREATE TABLE IF NOT EXISTS sales_data (
            id SERIAL PRIMARY KEY,
            sales_date DATE,
            product_id INT,
            product_name VARCHAR(255),
            quantity INT,
            price DECIMAL,
            category VARCHAR(255),
            ai_analytics_id SERIAL references ai_analytics(id)
            );""")
        finally:
            await conn.close()
