from config import *
import re
from locales import LOCALES, TEXT
import logging
import hashlib
import pymongo
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.message import ContentType
from aiogram.types import BotCommand
from aiogram.types.input_media import InputMedia, InputMediaPhoto, InputMediaVideo, \
    InputMediaAudio, InputMediaDocument, InputMediaAnimation
from aiogram.types.inline_query_result import InlineQueryResult, InlineQueryResultArticle, \
    InlineQueryResultCachedAudio, InlineQueryResultCachedDocument, InlineQueryResultCachedGif, \
    InlineQueryResultCachedMpeg4Gif, InlineQueryResultCachedPhoto, InlineQueryResultCachedVideo
from aiogram.dispatcher import filters

logging.basicConfig(level=logging.DEBUG)

client = pymongo.MongoClient(DB_URL)
db = client.kBinderDB

bot: Bot = Bot(token=TOKEN)
dp: Dispatcher = Dispatcher(bot)


def keyword_splitter(full_text: str):
    split_text = full_text.split(maxsplit=2)[1:]
    kwd, txt = split_text if len(split_text) == 2 else (split_text[0], '')
    substring = ''
    flag = False
    for ch in kwd[::-1]:
        if ch == '>':
            flag = True
        if flag:
            substring += ch
        if ch == '<':
            flag = False
            txt = substring[::-1] + txt
            substring = ''
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
    return keyword.lower(), text, raw_text


def insert_args(text: str, args: list = ()) -> str:
    var = r' @([\w]*) '
    edited_text = text
    for arg in args:
        if arg == '_':
            default = re.search(var, edited_text).groups()[0]
            edited_text = re.sub(var, f' {default} ' if default else ' ', edited_text, 1)
            continue
        edited_text = re.sub(var, f' {arg} ', edited_text, 1)
    while searched := re.search(var, edited_text):
        default = searched.groups()[0]
        edited_text = re.sub(var, f' {default} ' if default else ' ', edited_text, 1)
    edited_text = edited_text.replace(r' \@', ' @')
    return edited_text


def input_media(file: dict, text: str) -> InputMedia:
    type = file['type']
    file_id = file['file_id']
    params = {'caption': text, 'parse_mode': 'html'}
    if type == ContentType.PHOTO:
        return InputMediaPhoto(file_id, **params)
    if type == ContentType.VIDEO:
        return InputMediaVideo(file_id, **params)
    if type == ContentType.AUDIO:
        return InputMediaAudio(file_id, **params)
    if type == ContentType.DOCUMENT:
        return InputMediaDocument(file_id, **params)
    if type == ContentType.ANIMATION:
        return InputMediaAnimation(file_id, **params)


async def send_input_media_message(user_id: (int, str), text: str, file: (dict, None)) -> types.Message:
    type = file['type']
    file_id = file['file_id']
    params = {'chat_id': user_id, 'caption': text, 'parse_mode': 'html'}
    if type == ContentType.PHOTO:
        return await bot.send_photo(photo=file_id, **params)
    if type == ContentType.VIDEO:
        return await bot.send_video(video=file_id, **params)
    if type == ContentType.AUDIO:
        return await bot.send_audio(audio=file_id, **params)
    if type == ContentType.DOCUMENT:
        return await bot.send_document(document=file_id, **params)
    if type == ContentType.ANIMATION:
        return await bot.send_animation(animation=file_id, **params)


async def send_simple_answer(message: types.Message, variant: str, params: list = ()):
    locale = (message.from_user.language_code or 'en').split('-')[0]
    text = LOCALES['en'][variant] if locale not in LOCALES else LOCALES[locale][variant]
    await bot.send_message(chat_id=message.chat.id, text=text.format(*params), parse_mode='Markdown')


async def send_keyword_answer(user_id: (int, str), keywords: list):
    response = db.keywords.find({'user_id': user_id, 'key': keywords})
    content = list(response)[0]
    f_len = len(content['files'])
    text = insert_args(content['text'])
    if f_len > 1:
        media = types.MediaGroup()
        first = True
        for file in content['files'][:10]:
            media.attach(input_media(file, text if first else ''))
            first = False
        await bot.send_media_group(chat_id=user_id, media=media)
    elif f_len > 0:
        await send_input_media_message(user_id, text, content['files'][0])
    else:
        await bot.send_message(chat_id=user_id, text=text, parse_mode='html')


@dp.inline_handler()
async def inline_answers(inline_query: types.InlineQuery):
    try:
        (kwd, *args) = inline_query.query.split()
        kwd = kwd.lower()
    except ValueError:
        return
    query_id = inline_query.id
    user_id = inline_query['from'].id
    try:
        res = list(db.keywords.find(
            {'user_id': user_id, 'key': kwd}))[0]
    except IndexError:
        return
    f_len = len(res['files'])
    text = insert_args(res['text'], args)

    if f_len:
        items = []
        for file in res['files']:
            f_type = file['type']
            result_id: str = hashlib.md5((text + str(query_id) + file['file_id']).encode()).hexdigest()
            bind = {
                'id': result_id,
                'title': kwd,
                'caption': text,
                'description': res['raw_text'],
                'parse_mode': 'html',
            }
            item = None
            if f_type == ContentType.PHOTO:
                item = InlineQueryResultCachedPhoto(**bind, photo_file_id=file['file_id'])
            elif f_type == ContentType.VIDEO:
                item = InlineQueryResultCachedVideo(**bind, video_file_id=file['file_id'])
            elif f_type == ContentType.DOCUMENT:
                item = InlineQueryResultCachedDocument(**bind, document_file_id=file['file_id'])
            elif f_type == ContentType.ANIMATION:
                item = InlineQueryResultCachedMpeg4Gif(
                    id=result_id,
                    mpeg4_file_id=file['file_id'],
                    title=bind['title'],
                    caption=bind['caption'],
                    parse_mode='html',
                )
            elif f_type == ContentType.AUDIO:
                item = InlineQueryResultCachedAudio(
                    id=result_id,
                    audio_file_id=file['file_id'],
                    caption=text,
                    parse_mode='html',
                )
            items.append(item)
    else:
        result_id: str = hashlib.md5((text + str(query_id)).encode()).hexdigest()
        items = [InlineQueryResultArticle(
            id=result_id,
            title=text,
            description=res['raw_text'],
            input_message_content=types.InputTextMessageContent(
                text, parse_mode='html')
        )]
    for it in items:
        print(it)
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
    if len(res):
        text = '\n'.join(list(map(
            lambda kwd: f'`{", ".join(kwd["key"])}`: _{" ".join(kwd["raw_text"].split(maxsplit=4)[:3])}..._', res)))
        await send_simple_answer(message, TEXT.ON_LIST, [text])
    else:
        await send_simple_answer(message, TEXT.ON_LIST_EMPTY)


@dp.message_handler(filters.Command('bind', ignore_caption=False),
                    content_types=types.ContentTypes.ANY)
async def on_bind(message: types.Message):
    media_group = []
    if message.content_type != ContentType.TEXT:
        media_group = list(filter(lambda mess: mess.from_user.id == message.from_user.id,
                                  map(lambda upd: upd.message, await bot.get_updates())))
    is_media_group = bool(len(media_group))
    try:
        keyword, text, raw_text = keyword_splitter(message.html_text)
        keywords = keyword.split(',')
        bind = {
            'user_id': message.from_user.id,
            'key': keywords,
            'text': text,
            'raw_text': raw_text
        }
        if message.content_type == ContentType.TEXT:
            if text == '':
                raise ValueError

        msgs = media_group if is_media_group else [message]
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

        req = {'$or': []}
        for kwd in keywords:
            req['$or'].append({'key': kwd, 'user_id': message.from_user.id})
        matches = list(db.keywords.find(req))
        for match in matches:
            new_keys = list(set(match['key']) - set(keywords))
            if len(new_keys):
                db.keywords.update({'_id': match['_id']}, {'key': new_keys})
            else:
                db.keywords.delete_one({'_id': match['_id']})

        db.keywords.insert_one(bind)
    except (ValueError, IndexError):
        await send_simple_answer(message, TEXT.ON_BIND_ERROR)
    else:
        await send_keyword_answer(message.from_user.id, keywords)


@dp.message_handler(commands=['unbind'])
async def on_unbind(message: types.Message):
    user_id = message.from_user.id
    try:
        key: str = message.text.split(maxsplit=2)[1:3][0]
        matches = list(db.keywords.find({'user_id': user_id, 'key': key}))
        for match in matches:
            new_keys = [x for x in match['key'] if x != key]
            if len(new_keys):
                db.keywords.update_one({'_id': match['_id']}, {'$set': {'key': new_keys}})
            else:
                db.keywords.delete_one({'_id': match['_id']})
        if len(matches):
            await send_simple_answer(message, TEXT.ON_UNBIND_DELETE)
        else:
            raise IndexError
    except IndexError:
        await send_simple_answer(message, TEXT.ON_UNBIND_DELETE_ERROR)


async def on_startup(dispatch: Dispatcher):
    await bot.set_my_commands([
        BotCommand('bind', 'keyword your value - bind new keyword'),
        BotCommand('list', '- show all keywords'),
        BotCommand('help', '- additional information'),
        BotCommand('unbind', 'keyword - delete bound keyword'),
    ])


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
