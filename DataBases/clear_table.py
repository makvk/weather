import aiosqlite
import os

directory = "D:\\weather_bot\DataBases"
db_name = "subscribers.db"
db_path = os.path.join(directory, db_name)

async def clear_tb():
    async with aiosqlite.connect(db_path) as db:
        await db.execute(f"DELETE FROM users;")
        await db.commit()