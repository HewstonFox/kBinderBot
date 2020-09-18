from config import TOKEN
from locales import LOCALES, TEXT
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import filters

logging.basicConfig(level=logging.DEBUG)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


async def send_simple_answer(message: types.Message, variant: str):
    locale = (message.from_user.language_code or 'en').split('-')[0]
    text = LOCALES['en'][variant] if locale not in LOCALES else LOCALES[locale][variant]
    await bot.send_message(chat_id=message.chat.id, text=text, parse_mode='Markdown')


@dp.message_handler(commands=['help'])
async def on_help(message: types.Message):
    await send_simple_answer(message, TEXT.on_help)


@dp.message_handler(commands=['start'])
async def on_start(message: types.Message):
    await send_simple_answer(message, TEXT.on_start)


@dp.message_handler(filters.Command('bind', ignore_caption=False),
                    content_types=types.ContentTypes.ANY)
async def on_bind(message: types.Message):
    media_group = []
    if message.media_group_id:
        media_group = list(filter(lambda msg: msg.media_group_id == message.media_group_id,
                                  map(lambda upd: upd.message, await bot.get_updates())))
    for med in media_group:
        print(med)
    keyword, text = message.html_text.split(maxsplit=2)[1:]
    print(keyword, ':', text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
