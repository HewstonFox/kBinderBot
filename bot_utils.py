import re
import hashlib

from aiogram.types import \
    Update, \
    Message, \
    InputMedia, \
    ContentType, \
    CallbackQuery, \
    InputMediaPhoto, \
    InputMediaVideo, \
    InputMediaAudio, \
    InlineQueryResult, \
    InputMediaDocument, \
    InputMediaAnimation, \
    InlineKeyboardButton, \
    InlineKeyboardMarkup, \
    InputTextMessageContent, \
    InlineQueryResultArticle, \
    InlineQueryResultCachedAudio, \
    InlineQueryResultCachedPhoto, \
    InlineQueryResultCachedVideo, \
    InlineQueryResultCachedDocument, \
    InlineQueryResultCachedMpeg4Gif
from typing import List, Union
from bot_types import BindRecord, BindFile, ACTION


def keyword_splitter(full_text: str) -> tuple:
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
    var = r'(?=[^\\])(\W|^)@(\w*)(\W|$)'
    edited_text = text
    for arg in args:
        try:
            left, default, right = re.search(var, edited_text).groups()
        except (ValueError, AttributeError):
            break
        if not default and right == left == ' ' and arg == '_':
            right = ''
        edited_text = re.sub(var, f'{left}{default if arg == "_" else arg}{right}', edited_text, 1)
    while searched := re.search(var, edited_text):
        left, default, right = searched.groups()
        edited_text = re.sub(var, f'{left}{default}{right}' if default else ' ', edited_text, 1)
    excludes = r'(\W|^)\\(@|_)(\W|$)'
    while searched := re.search(excludes, edited_text):
        left, value, right = searched.groups()
        edited_text = re.sub(excludes, f'{left}{value}{right}', edited_text, 1)
    edited_text = edited_text.replace(r' \@', ' @')
    return edited_text


def input_media(file: dict, text: str) -> InputMedia:
    f_type = file['type']
    file_id = file['file_id']
    params = {'caption': text}
    if f_type == ContentType.PHOTO:
        return InputMediaPhoto(file_id, **params)
    if f_type == ContentType.VIDEO:
        return InputMediaVideo(file_id, **params)
    if f_type == ContentType.AUDIO:
        return InputMediaAudio(file_id, **params)
    if f_type == ContentType.DOCUMENT:
        return InputMediaDocument(file_id, **params)
    if f_type == ContentType.ANIMATION:
        return InputMediaAnimation(file_id, **params)


def get_message_file_id_and_type(message: Message) -> (Union[str, None], ContentType):
    message_type = message.content_type
    file_id = None
    if message_type == ContentType.PHOTO:
        file_id = message.photo[0].file_id
    if message_type == ContentType.VIDEO:
        file_id = message.video.file_id
    if message_type == ContentType.ANIMATION:
        file_id = message.animation.file_id
    if message_type == ContentType.AUDIO:
        file_id = message.audio.file_id
    if message_type == ContentType.DOCUMENT:
        file_id = message.document.file_id

    return file_id, message_type


def message2bind_record_with_keys(message: Message, updates: List[Update]) -> (BindRecord, List[str]):
    keyword, text, raw_text = keyword_splitter(message.html_text)

    message_group: List[Message] = list(filter(
        lambda mess: mess.from_user.id == message.from_user.id,
        map(lambda upd: upd.message, updates)
    ))
    if message.content_type == ContentType.TEXT and text == '':
        raise ValueError

    keys = keyword.split(',')

    files: List[BindFile] = []

    bind = BindRecord(**{
        'text': text,
        'raw_text': raw_text,
        'files': files
    })

    for msg in message_group:
        (file_id, msg_type) = get_message_file_id_and_type(msg)
        if msg_type != ContentType.TEXT:
            files.append({
                'file_id': file_id,
                'type': msg_type
            })

    return bind, keys


def create_query_results(query_id: str, key: str, bind: BindRecord, args) -> List[InlineQueryResult]:
    text = insert_args(bind['text'], args)

    if len(bind['files']):
        results = []
        for file in bind['files']:
            f_type = file['type']
            result_id: str = hashlib.md5((text + query_id + file['file_id']).encode()).hexdigest()
            result = {
                'id': result_id,
                'title': key,
                'caption': text,
                'description': bind['raw_text']
            }
            if f_type == ContentType.PHOTO:
                item = InlineQueryResultCachedPhoto(**result, photo_file_id=file['file_id'])
            elif f_type == ContentType.VIDEO:
                item = InlineQueryResultCachedVideo(**result, video_file_id=file['file_id'])
            elif f_type == ContentType.DOCUMENT:
                item = InlineQueryResultCachedDocument(**result, document_file_id=file['file_id'])
            elif f_type == ContentType.ANIMATION:
                item = InlineQueryResultCachedMpeg4Gif(
                    id=result_id,
                    mpeg4_file_id=file['file_id'],
                    title=result['title'],
                    caption=result['caption'],
                )
            elif f_type == ContentType.AUDIO:
                item = InlineQueryResultCachedAudio(
                    id=result_id,
                    audio_file_id=file['file_id'],
                    caption=text,
                )
            else:
                continue
            results.append(item)
    else:
        result_id: str = hashlib.md5((text + str(query_id)).encode()).hexdigest()
        results = [InlineQueryResultArticle(
            id=result_id,
            title=text,
            description=bind['raw_text'],
            input_message_content=InputTextMessageContent(text)
        )]

    return results


def create_keywords_keyboard(user_id: (int, str), keywords: List, chink_size: int = 2) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            list(map(
                lambda key: InlineKeyboardButton(key, callback_data=f'{ACTION.SHOW} {user_id} {key}'),
                keywords[i:i + chink_size]
            ))
            for i in range(0, len(keywords), chink_size)
        ])


def unpack_keyword_query_data(query: CallbackQuery) -> (str, (int, str), [str]):
    (action, user_id, *meta) = query.data.split()
    return action, int(user_id), meta
