from datetime import datetime, timedelta
from typing import Annotated

from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from jose import JWTError, jwt
from fastapi import HTTPException, Depends
from starlette import status
from starlette.status import HTTP_400_BAD_REQUEST
from controllers.config import SECRET_KEY as KEY, ALGORITHM as ALG, ACCESS_TOKEN_EXPIRE_MINUTES as EXP
from db.database import db
from schemas.schemas import UserAuth, TokenData
from secure import pwd_context

SECRET_KEY = KEY
ALGORITHM = ALG
ACCESS_TOKEN_EXPIRE_MINUTES = EXP
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(secret_token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(secret_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(id=user_id)
    except JWTError:
        raise credentials_exception
    user = await db.get_user_by_id(token_data.id)
    if user is None:
        raise credentials_exception

    return user

async def token(user_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await db.select_user_email(user_data.username)
    if not user:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail='User not found'
        )
    if not pwd_context.verify(user_data.password, user["password"]):
        raise HTTPException(
            status_code=400,
            detail='Incorrect username or password'
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["id"])}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


async def get_user_by_token(access_token: str):
    second = datetime.datetime.now().timestamp()
    secret_token = await db.get_record_by_token(access_token)
    if secret_token and abs(second - secret_token['created_at']) < secret_token['exp']:
        return await db.get_user_by_id(secret_token["user_id"])
    else:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail='Unauthorized'
        )

