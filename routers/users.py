from typing import List, Annotated
from fastapi import APIRouter, Depends

from controllers.tokens import get_user_by_token, token, get_current_user
from controllers.users import register
from schemas.schemas import User, UserCreate, BaseUser, LiteUser, UserAuth
from secure import apikey_scheme

router = APIRouter()


@router.post("", response_model=User, status_code=201)
async def register_user(user_data: UserCreate):
    response = await register(user_data)
    return response

@router.post("/self", response_model=LiteUser, status_code=201)
async def read_self(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


