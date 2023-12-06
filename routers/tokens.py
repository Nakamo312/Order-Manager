from typing import List, Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from controllers.tokens import token
from schemas.schemas import Token, UserAuth

router = APIRouter()


@router.post("", response_model=Token, status_code=201)
async def create_token(user_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    response = await token(user_data)
    return response
