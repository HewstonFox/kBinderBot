from functools import wraps
from typing import List, Callable, Dict

import pymongo
from aiogram.types import User
from pymongo.results import InsertOneResult

from bot_types import BindRecord, UserRecord, DocumentNotFoundError, KeywordNotFoundError
from config import DB_URL

client = pymongo.MongoClient(DB_URL)
db = client.kBinderDB


def raise_no_document(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        if res:
            return res
        raise DocumentNotFoundError

    return wrapper


@raise_no_document
def get_user(user_id: (int, str)) -> UserRecord:
    return db.users.find_one({'user_id': user_id})


def update_user(user: User) -> UserRecord:
    db.users.update_one(
        {'user_id': user.id},
        {
            '$setOnInsert': {
                'user_id': user.id,
                'keywords': {}
            },
            '$set': {
                'full_name': user.full_name,
                'username': user.username,
            }
        },
        upsert=True
    )
    return get_user(user.id)


def update_user_keywords(user_id: (int, str), keywords: Dict[str, str]):
    if keywords:
        db.users.update_one(
            {'user_id': user_id},
            {'$set': {'keywords': keywords}}
        )
    else:
        db.users.delete_one({'user_id': user_id})


def remove_keyword(user_id: (int, str), key: str):
    user_record = get_user(user_id)
    try:
        keywords = user_record['keywords']
        bind_id = keywords.pop(key)
        update_user_keywords(user_id, keywords)
    except KeyError:
        raise KeywordNotFoundError
    if bind_id not in user_record['keywords'].values():
        db.keywords.delete_one({'_id': bind_id})


def insert_keyword(user: User, record: BindRecord, keys: List[str]):
    user_record = update_user(user)
    for key in keys:
        if key in user_record['keywords']:
            remove_keyword(user.id, key)
    record_result: InsertOneResult = db.keywords.insert_one(record)
    keywords = user_record['keywords']
    for key in keys:
        keywords[key] = record_result.inserted_id
    update_user_keywords(user.id, keywords)


def get_user_keywords(user_id: (int, str)) -> List[str]:
    user_record = get_user(user_id)
    return list(user_record['keywords'].keys())


@raise_no_document
def get_bind(user_id: (int, str), kwd: str) -> BindRecord:
    user_record = get_user(user_id)
    try:
        bind_id = user_record['keywords'][kwd]
    except KeyError:
        raise DocumentNotFoundError
    return db.keywords.find_one({'_id': bind_id})
