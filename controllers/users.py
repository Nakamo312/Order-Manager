from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

from db.database import db
from schemas.schemas import UserCreate
from secure import pwd_context


async def register(user_data: UserCreate):
    if await db.select_user_email(user_data.email):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail='User with this email already exists'
        )
    user_data.password = pwd_context.hash(user_data.password)
    await db.add_user(user_data.name, user_data.email, user_data.password)
    return await db.select_user_email(user_data.email)

