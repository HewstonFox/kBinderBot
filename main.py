import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import BotCommand
from aiogram.types.message import ContentType
from aiogram.dispatcher import filters
from aiogram.contrib.middlewares.i18n import I18nMiddleware
from bot_types import KeywordNotFoundError, DocumentNotFoundError
from config import TOKEN, I18N_DOMAIN, LOCALES_DIR
from db import remove_keyword, insert_keyword, get_user_keywords, get_bind
from locales import TEXT
from bot_utils import \
    insert_args, \
    input_media, \
    create_query_results, \
    create_keywords_keyboard, \
    unpack_keyword_query_data, \
    message2bind_record_with_keys

logging.basicConfig(level=logging.INFO)

bot: Bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp: Dispatcher = Dispatcher(bot)

i18n = I18nMiddleware(I18N_DOMAIN, LOCALES_DIR)
dp.middleware.setup(i18n)

t = i18n.gettext


async def send_input_media_message(user_id: (int, str), text: str, file: (dict, None)) -> types.Message:
    f_type = file['type']
    file_id = file['file_id']
    params = {'chat_id': user_id, 'caption': text}
    if f_type == ContentType.PHOTO:
        return await bot.send_photo(photo=file_id, **params)
    if f_type == ContentType.VIDEO:
        return await bot.send_video(video=file_id, **params)
    if f_type == ContentType.AUDIO:
        return await bot.send_audio(audio=file_id, **params)
    if f_type == ContentType.DOCUMENT:
        return await bot.send_document(document=file_id, **params)
    if f_type == ContentType.ANIMATION:
        return await bot.send_animation(animation=file_id, **params)


async def send_keyword_answer(user_id: (int, str), key: str, raw: bool = False, query_id: str = None):
    try:
        bind = get_bind(user_id, key)
    except DocumentNotFoundError:
        if query_id:
            await bot.answer_callback_query(query_id, t(TEXT.BIND.NOT_FOUND))
        return
    f_len = len(bind['files'])
    text = bind['raw_text'] if raw else insert_args(bind['text'])
    if f_len > 1:
        media = types.MediaGroup()
        first = True
        for file in bind['files'][:10]:
            media.attach(input_media(file, text if first else ''))
            first = False
        await bot.send_media_group(chat_id=user_id, media=media)
    elif f_len > 0:
        await send_input_media_message(user_id, text, bind['files'][0])
    else:
        await bot.send_message(chat_id=user_id, text=text)


@dp.callback_query_handler()
async def callback_query_answer(query: types.CallbackQuery):
    await send_keyword_answer(*unpack_keyword_query_data(query), True, query.id)
    await bot.answer_callback_query(query.id)


@dp.inline_handler()
async def inline_answers(inline_query: types.InlineQuery):
    try:
        (key, *args) = inline_query.query.split()
        key = key.lower()
    except ValueError:
        return

    query_id = inline_query.id

    try:
        bind = get_bind(inline_query['from'].id, key)
    except DocumentNotFoundError:
        await bot.answer_inline_query(
            query_id,
            results=[],
            switch_pm_text=t(TEXT.BUTTON.BIND_KEYWORD),
            switch_pm_parameter=key
        )
        return

    await bot.answer_inline_query(
        query_id,
        results=create_query_results(query_id, key, bind, args),
        is_personal=True,
        cache_time=1
    )


@dp.message_handler(commands=['help'])
async def on_help(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text=t(TEXT.COMMAND.HELP))


@dp.message_handler(commands=['start'])
async def on_start(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text=t(TEXT.COMMAND.START))


@dp.message_handler(commands=['list'])
async def on_list(message: types.Message):
    await bot.send_chat_action(message.chat.id, 'typing')
    try:
        user_id = message.from_user.id
        keys = get_user_keywords(user_id)
        if not len(keys):
            raise DocumentNotFoundError
        keyboard = create_keywords_keyboard(user_id, keys)
        await bot.send_message(
            chat_id=message.chat.id,
            text=t(TEXT.COMMAND.LIST),
            reply_markup=keyboard
        )
    except DocumentNotFoundError:
        await bot.send_message(chat_id=message.chat.id, text=t(TEXT.COMMAND.LIST_EMPTY))


@dp.message_handler(filters.Command('bind', ignore_caption=False), content_types=types.ContentTypes.ANY)
async def on_bind(message: types.Message):
    try:
        (bind, keys) = message2bind_record_with_keys(message, await bot.get_updates())
        insert_keyword(message.from_user, bind, keys)
    except (ValueError, IndexError):
        await bot.send_message(chat_id=message.chat.id, text=t(TEXT.BIND.ERROR))
    else:
        await send_keyword_answer(message.from_user.id, keys[0])


@dp.message_handler(commands=['unbind'])
async def on_unbind(message: types.Message):
    try:
        key: str = message.text.split(maxsplit=2)[1:3][0].lower()
        remove_keyword(message.from_user.id, key)
    except (KeywordNotFoundError, IndexError):
        await bot.send_message(chat_id=message.chat.id, text=t(TEXT.KEYWORD.DELETE.ERROR))
    else:
        await bot.send_message(chat_id=message.chat.id, text=t(TEXT.KEYWORD.DELETE.SUCCESS))


async def on_startup(dispatch: Dispatcher):
    await bot.set_my_commands([
        BotCommand('bind', 'keyword your value - bind new keyword'),
        BotCommand('list', '- show all keywords'),
        BotCommand('help', '- additional information'),
        BotCommand('unbind', 'keyword - delete bound keyword'),
    ])


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
