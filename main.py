import asyncio
import random
import string
import aiosqlite

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

from config import BOT_TOKEN, BOT_USERNAME
from database import init_db

bot = Bot(token=8733248197:AAEhO2-dsuwjpDqQdDf5ZdncCT8XzDM2nsU)
dp = Dispatcher()

DB = "data/bot.db"

# =====================
# MEMORY (кому пишемо)
# =====================
dp.target = {}


# =====================
# CODE
# =====================
def code():
    return "".join(random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(7))


# =====================
# USER
# =====================
async def get_or_create(user_id):
    async with aiosqlite.connect(DB) as db:
        r = await db.execute("SELECT code FROM users WHERE telegram_id=?", (user_id,))
        row = await r.fetchone()

        if row:
            return row[0]

        c = code()

        await db.execute(
            "INSERT INTO users (telegram_id, code) VALUES (?, ?)",
            (user_id, c)
        )
        await db.commit()

        return c


async def get_user(code_):
    async with aiosqlite.connect(DB) as db:
        r = await db.execute("SELECT telegram_id FROM users WHERE code=?", (code_,))
        row = await r.fetchone()
        return row[0] if row else None


# =====================
# BAN SYSTEM
# =====================
async def is_banned(owner, sender):
    async with aiosqlite.connect(DB) as db:
        r = await db.execute(
            "SELECT 1 FROM bans WHERE owner=? AND banned=?",
            (owner, sender)
        )
        return await r.fetchone() is not None


# =====================
# START
# =====================
@dp.message(Command("start"))
async def start(m: Message):
    args = m.text.split()

    if len(args) > 1:
        c = args[1]
        target = await get_user(c)

        if target:
            dp.target[m.from_user.id] = target
            await m.answer("💌 напиши анонімне повідомлення:")
            return

    c = await get_or_create(m.from_user.id)

    await m.answer(
        f"👤 твій профіль\n\n"
        f"🔗 https://t.me/{ihatekaddbot}?start={c}"
    )


# =====================
# PROFILE
# =====================
@dp.message(Command("profile"))
async def profile(m: Message):
    c = await get_or_create(m.from_user.id)

    await m.answer(
        f"👤 профіль\n"
        f"🔗 https://t.me/{ihatekaddbot}?start={c}"
    )


# =====================
# LINK
# =====================
@dp.message(Command("link"))
async def link(m: Message):
    c = await get_or_create(m.from_user.id)

    await m.answer(f"https://t.me/{ihatekaddbot}?start={c}")


# =====================
# BAN
# =====================
@dp.message(Command("ban"))
async def ban(m: Message):
    args = m.text.split()

    if len(args) < 2:
        return await m.answer("використання: /ban")

    banned = int(args[1])

    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "INSERT INTO bans (owner, banned) VALUES (?, ?)",
            (m.from_user.id, banned)
        )
        await db.commit()

    await m.answer("🚫 заблоковано")


# =====================
# UNBAN
# =====================
@dp.message(Command("unban"))
async def unban(m: Message):
    args = m.text.split()

    if len(args) < 2:
        return await m.answer("використання: /unban")

    banned = int(args[1])

    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "DELETE FROM bans WHERE owner=? AND banned=?",
            (m.from_user.id, banned)
        )
        await db.commit()

    await m.answer("✔ розблоковано")


# =====================
# MESSAGES
# =====================
@dp.message()
async def msg(m: Message):
    uid = m.from_user.id

    if uid not in dp.target:
        return

    target = dp.target[uid]

    if await is_banned(target, uid):
        return await m.answer("вас заблоковано 🚫")

    text = m.text

    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "INSERT INTO messages (sender, receiver, text) VALUES (?, ?, ?)",
            (uid, target, text)
        )
        await db.commit()

    await bot.send_message(
        target,
        f"💌 анонім:\n{text}"
    )

    await m.answer("надіслано 💌")

    del dp.target[uid]


# =====================
# RUN
# =====================
async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
