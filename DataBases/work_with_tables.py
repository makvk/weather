import aiosqlite
import os
from typing import List, Dict
import logging

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

directory = "./DataBases/"
db_name = "subscribers.db"
db_path = os.path.join(directory, db_name)

async def create_table_if_not_exists() -> None:
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        city TEXT NOT NULL,
        time TEXT NOT NULL
    )
    """
    try:
        async with aiosqlite.connect(db_path) as con:
            await con.execute(create_table_sql)
            await con.commit()
    except Exception as e:
        logger.error(f"Ошибка при создании таблицы: {e}")
        raise

async def add_to_table(user_id: int, city: str, time: str) -> None:
    try:
        async with aiosqlite.connect(db_path) as con:  # Автоматическое закрытие соединения
            await con.execute(
                "INSERT OR REPLACE INTO users (user_id, city, time) VALUES (?, ?, ?)",
                (user_id, city, time)
            )
            await con.commit() 
    except Exception as e:
        logger.error(f"Ошибка при добавлении пользователя {user_id}: {e}")
        raise

async def remove_subscriber(user_id: int) -> None:
    try: 
        async with aiosqlite.connect(db_path) as con:
            await con.execute(
                "DELETE FROM users WHERE user_id = ?", 
                (user_id,)
            )
            await con.commit()
    except Exception as e:
        logger.error(f"Ошибка при удалении пользователя {user_id}: {e}")
        raise

async def get_all_subscribers() -> List[Dict]:
    try:
        async with aiosqlite.connect(db_path) as con:
            async with con.cursor() as cur:  
                await cur.execute("SELECT user_id, city, time FROM users")
                rows = await cur.fetchall()
                subscribers = [
                    {"user_id": row[0], "city": row[1], "send_time": row[2]}
                    for row in rows
                ]
        return subscribers
    except Exception as e:
        logger.error(f"Ошибка при получении списка пользователей: {e}")
        raise

