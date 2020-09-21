from config import TOKEN
from locales import LOCALES, TEXT
from mongodb import db
import logging
import hashlib
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.message import ContentType
from aiogram.types.input_media import InputMediaPhoto, InputMediaVideo
from aiogram.dispatcher import filters

logging.basicConfig(level=logging.DEBUG)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


def keyword_splitter(full_text):
    splited = full_text.split(maxsplit=2)[1:]
    kwd, txt = splited if len(splited) == 2 else (splited[0], '')
    substr = ''
    flag = False
    for ch in kwd[::-1]:
        if ch == '>':
            flag = True
        if flag:
            substr += ch
        if ch == '<':
            flag = False
            txt = substr[::-1] + txt
            substr = ''
    keyword = ''
    flag = True
    for ch in kwd:
        if ch == '<':
            flag = False
        if flag:
            keyword += ch
        if ch == '>':
            flag = True
    text = ''
    i = 0
    while i < len(txt):
        if txt[i] == '<':
            tag_close_id = txt.find('>', i)
            if len(txt) > tag_close_id + 3:
                if txt[tag_close_id + 1:tag_close_id + 3] == '</':
                    tag_end_id = txt.find('>', tag_close_id + 2)
                    i = tag_end_id + 1
                    continue
        text += txt[i]
        i += 1
    raw_text = ''
    flag = True
    for ch in text:
        if ch == '<':
            flag = False
        if flag:
            raw_text += ch
        if ch == '>':
            flag = True
    return (keyword, text, raw_text)


async def send_simple_answer(message: types.Message, variant: str, params: list = []):
    locale = (message.from_user.language_code or 'en').split('-')[0]
    text = LOCALES['en'][variant] if locale not in LOCALES else LOCALES[locale][variant]
    await bot.send_message(chat_id=message.chat.id, text=text.format(*params), parse_mode='Markdown')


async def send_keyword_answer(user_id, keyword):
    response = db.keywords.find({'user_id': user_id, 'key': keyword})
    content = list(response)[0]
    f_len = len(content['files'])
    if f_len > 1:
        media = types.MediaGroup()
        first = True
        for file in content['files']:
            if file['type'] == ContentType.PHOTO:
                media.attach_photo(
                    InputMediaPhoto(file['file_id'], parse_mode='html', caption=content['text'] if first else ''))
            elif file['type'] == ContentType.VIDEO:
                media.attach_video(
                    InputMediaVideo(file['file_id'], parse_mode='html', caption=content['text'] if first else ''))
            first = False
        await bot.send_media_group(chat_id=user_id, media=media)
    elif f_len == 1:
        file = content['files'][0]
        f_type = file['type']
        if f_type == ContentType.PHOTO:
            await bot.send_photo(chat_id=user_id,
                                 photo=file['file_id'], caption=content['text'], parse_mode='html')
        if f_type == ContentType.VIDEO:
            await bot.send_video(chat_id=user_id,
                                 video=file['file_id'], caption=content['text'], parse_mode='html')
        if f_type == ContentType.ANIMATION:
            await bot.send_animation(
                chat_id=user_id, animation=file['file_id'], caption=file['text'], parse_mode='html')
        if f_type == ContentType.AUDIO:
            await bot.send_audio(chat_id=user_id,
                                 audio=file['file_id'], caption=content['text'], parse_mode='html')
        if f_type == ContentType.DOCUMENT:
            await bot.send_document(
                chat_id=user_id, document=file['file_id'], caption=content['text'],  parse_mode='html')
    else:
        await bot.send_message(
            chat_id=user_id, text=content['text'], parse_mode='html')


@dp.inline_handler()
async def inline_answers(inline_query: types.InlineQuery):
    text = inline_query.query
    query_id = inline_query.id
    user_id = inline_query['from'].id
    try:
        res = list(db.keywords.find({'user_id': user_id, 'key': text}))[0]
        print(res)
    except IndexError:
        return
    f_len = len(res['files'])
    text = res['text']
    alternate = types.InputTextMessageContent(text, parse_mode='html')
    if f_len:
        items = []
        for file in res['files']:
            f_type = file['type']
            result_id: str = hashlib.md5((text+str(query_id)+file['file_id']).encode()).hexdigest()
            semple = {
                'id': result_id,
                'title': ' '.join(res['raw_text'].split(maxsplit=4)[:4]),
                'caption': text,
                'description': res['raw_text'],
                'parse_mode': 'html',
            }
            if f_type == ContentType.PHOTO:
                item = types.InlineQueryResultCachedPhoto(
                    **semple,
                    photo_file_id=file['file_id'],
                )
            if f_type == ContentType.VIDEO:
                item = types.InlineQueryResultCachedVideo(
                    **semple,
                    video_file_id=file['file_id'],
                )
            if f_type == ContentType.ANIMATION:
                item = types.InlineQueryResultCachedMpeg4Gif(
                    id=result_id,
                    mpeg4_file_id=file['file_id'],
                    title=semple['title'],
                    caption=semple['caption'],
                    parse_mode='html',
                )
            if f_type == ContentType.AUDIO:
                item = types.InlineQueryResultCachedAudio(
                    id=result_id,
                    audio_file_id=file['file_id'],
                    caption=text,
                    parse_mode='html',
                )
            if f_type == ContentType.DOCUMENT:
                item = types.InlineQueryResultCachedDocument(
                    **semple,
                    document_file_id=file['file_id'],
                )
            items.append(item)
    else:
        result_id: str = hashlib.md5((text+str(query_id)).encode()).hexdigest()
        items = [types.InlineQueryResultArticle(
            id=result_id,
            title=res['text'],
            input_message_content=alternate
        )]
    await bot.answer_inline_query(query_id, results=items, is_personal=True, cache_time=1)


@dp.message_handler(commands=['help'])
async def on_help(message: types.Message):
    await send_simple_answer(message, TEXT.ON_HELP)


@dp.message_handler(commands=['start'])
async def on_start(message: types.Message):
    await send_simple_answer(message, TEXT.ON_START)


@dp.message_handler(commands=['list'])
async def on_list(message: types.Message):
    user_id = message.from_user.id
    res = list(db.keywords.find({'user_id': user_id}))
    text = '\n'.join(list(map(
        lambda kwd: f'`{kwd["key"]}`: *{" ".join(kwd["raw_text"].split(maxsplit=4)[:3])}...*', res)))
    await send_simple_answer(message, TEXT.ON_LIST, [text])


@dp.message_handler(filters.Command('bind', ignore_caption=False),
                    content_types=types.ContentTypes.ANY)
async def on_bind(message: types.Message):
    media_group = []
    if message.media_group_id:
        media_group = list(filter(lambda msg: msg.media_group_id == message.media_group_id,
                                  map(lambda upd: upd.message, await bot.get_updates())))
    is_media_goup = bool(len(media_group))
    try:
        keyword, text, raw_text = keyword_splitter(message.html_text)
        bind = {
            'user_id': message.from_user.id,
            'key': keyword,
            'text': text,
            'raw_text': raw_text
        }
        if message.content_type == ContentType.TEXT:
            if text == '':
                raise ValueError

        msgs = media_group if is_media_goup else [message]
        files = []
        for msg in msgs:
            msg_type = msg.content_type
            if msg_type == ContentType.PHOTO:
                files.append(
                    {'file_id': msg.photo[0].file_id, 'type': ContentType.PHOTO})
            if msg_type == ContentType.VIDEO:
                files.append(
                    {'file_id': msg.video.file_id, 'type': ContentType.VIDEO})
            if msg_type == ContentType.ANIMATION:
                files.append(
                    {'file_id': msg.animation.file_id, 'type': ContentType.ANIMATION})
            if msg_type == ContentType.AUDIO:
                files.append(
                    {'file_id': msg.audio.file_id, 'type': ContentType.AUDIO})
            if msg_type == ContentType.DOCUMENT:
                files.append(
                    {'file_id': msg.document.file_id, 'type': ContentType.DOCUMENT})
        bind['files'] = files
        db.keywords.delete_one(
            {'user_id': message.from_user.id, 'key': keyword})
        db.keywords.insert_one(bind)
        await send_keyword_answer(message.from_user.id, keyword)
    except (ValueError, IndexError):
        if len(message.html_text.split(maxsplit=1)) == 0:
            await send_simple_answer(message, TEXT.ON_BIND_ERROR)
        else:
            try:
                db.keywords.delete_one(
                    {'user_id': message.from_user.id, 'key': keyword})
                await send_simple_answer(message, TEXT.ON_BIND_DELETE)
            except UnboundLocalError:
                await send_simple_answer(message, TEXT.ON_BIND_DELETE_ERROR)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
