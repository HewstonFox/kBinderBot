from typing import TypedDict, List, Dict, Union
from aiogram.types.message import ContentType
from pymongo.collection import ObjectId


class BindFile(TypedDict):
    file_id: str
    type: ContentType


class BindRecord(TypedDict):
    text: str
    raw_text: str
    files: List[BindFile]


class UserRecord(TypedDict):
    _id: ObjectId
    user_id: Union[int, str]
    full_name: str
    username: str
    keywords: Dict[str, str]


class DocumentNotFoundError(Exception):
    """Document not exist in collection"""
    pass


class KeywordNotFoundError(Exception):
    """Keyword not found"""
    pass
