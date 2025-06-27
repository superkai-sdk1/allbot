from aiogram import Bot, Dispatcher, types
from aiogram.filters import Text
from aiogram.types import Message
from aiogram import F
import asyncio

API_TOKEN = '7523283669:AAGzK1tGLYK3ogHhNpWRUHrGVyrhkg0CAoY'

bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher()

@dp.message(Text(contains='@all'))
async def mention_all(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    member = await bot.get_chat_member(chat_id, user_id)
    if member.status not in ['administrator', 'creator']:
        await message.reply("❌ Только администраторы могут использовать @all")
        return

    mentions = []
    try:
        async for m in bot.iter_chat_members(chat_id):
            u = m.user
            if u.is_bot:
                continue
            name = (u.first_name or "")[:32]
            mentions.append(f'<a href="tg://user?id={u.id}">{name}</a>')
        if not mentions:
            return await message.reply("В группе нет подходящих пользователей.")
        batch = mentions[:30]
        await message.reply(" ".join(batch))
    except Exception as e:
        await message.reply(f"❗ Ошибка при упоминании: {e}")

async def main():
    dp.include_router(dp)
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
