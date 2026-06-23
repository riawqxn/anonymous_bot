import aiosqlite

DB = "data/bot.db"


async def init_db():
    async with aiosqlite.connect(DB) as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            code TEXT UNIQUE
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender INTEGER,
            receiver INTEGER,
            text TEXT
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS bans (
            owner INTEGER,
            banned INTEGER
        )
        """)

        await db.commit()
