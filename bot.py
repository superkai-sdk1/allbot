from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties
from aiogram.types import Message
import asyncio
import json
import os

API_TOKEN = '7523283669:AAGzK1tGLYK3ogHhNpWRUHrGVyrhkg0CAoY'
USERS_FILE = 'tracked_users.json'

bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Загружаем сохранённый список пользователей или создаём пустой
if os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        tracked_users = set(json.load(f))
else:
    tracked_users = set()

def save_users():
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(tracked_users), f, ensure_ascii=False, indent=2)

# Автоматически добавляем пользователей в tracked_users при любом сообщении
@dp.message()
async def track_users(message: Message):
    user = message.from_user
    if user and not user.is_bot:
        if user.id not in tracked_users:
            tracked_users.add(user.id)
            save_users()

@dp.message()
async def mention_all(message: Message):
    text = message.text or ""
    if '@all' not in text:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id

    member = await bot.get_chat_member(chat_id, user_id)
    if member.status not in ['administrator', 'creator']:
        await message.reply("❌ Только администраторы могут использовать @all")
        return

    mentions = []
    unique_ids = set()

    try:
        # Добавляем админов в упоминания
        admins = await bot.get_chat_administrators(chat_id)
        for admin in admins:
            u = admin.user
            if u.is_bot:
                continue
            if u.id not in unique_ids:
                name = (u.first_name or "")[:32]
                mentions.append(f'<a href="tg://user?id={u.id}">{name}</a>')
                unique_ids.add(u.id)

        # Добавляем всех сохранённых пользователей (если они в чате)
        for uid in tracked_users:
            if uid in unique_ids:
                continue
            try:
                member = await bot.get_chat_member(chat_id, uid)
                u = member.user
                if u.is_bot:
                    continue
                name = (u.first_name or "")[:32]
                mentions.append(f'<a href="tg://user?id={u.id}">{name}</a>')
                unique_ids.add(uid)
            except Exception:
                # Если пользователь вышел из чата или ошибка, пропускаем
                continue

        if not mentions:
            return await message.reply("В группе нет подходящих пользователей.")

        # Ограничим по 30 упоминаний в одном сообщении
        batch_size = 30
        for i in range(0, len(mentions), batch_size):
            batch = mentions[i:i+batch_size]
            await message.reply(" ".join(batch))

    except Exception as e:
        await message.reply(f"❗ Ошибка при упоминании: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
