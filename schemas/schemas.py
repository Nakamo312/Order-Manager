from datetime import datetime, date

from pydantic import BaseModel, EmailStr
from typing import List
from enum import Enum


class BaseUser(BaseModel):
    name: str
    email: EmailStr


class UserCreate(BaseUser):
    password: str


class UserAuth(BaseModel):
    name: EmailStr
    password: str


class LiteUser(BaseUser):
    id: int


class User(UserCreate):
    id: int


class Status(Enum):
    open = "open"
    vip = "VIP"
    closed = "closed"


class ProposeCreate(BaseModel):
    title: str
    status: Status


class BasePropose(ProposeCreate):
    created_at: datetime


class Propose(BasePropose):
    id: int
    name: str
    user_id: int


class BaseResponse(BaseModel):
    text: str


class Response(BaseResponse):
    id: int
    user_id: int
    propose_id: int
    created_at: datetime


class ProposePage(BaseModel):
    propose: Propose
    response: List[Response]


class Dialog(BaseModel):
    id: int
    text: str
    response_id: int
    user_id: int


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: int
