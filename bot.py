
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

API_TOKEN = '7523283669:AAGzK1tGLYK3ogHhNpWRUHrGVyrhkg0CAoY'

bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

@dp.message_handler(lambda msg: '@all' in (msg.text or ''))
async def mention_all(message: types.Message):
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

if __name__ == '__main__':
    executor.start_polling(dp)
