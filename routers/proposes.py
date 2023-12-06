from datetime import datetime
from typing import List, Annotated
from fastapi import APIRouter, Depends

from controllers.tokens import get_user_by_token, get_current_user
from db.database import db
from schemas.schemas import Propose, Response, BasePropose, BaseResponse, Dialog, ProposePage, User, ProposeCreate
from secure import apikey_scheme

router = APIRouter()


@router.post("", response_model=BasePropose, status_code=201)
async def submit_propose(current_user: Annotated[User, Depends(get_current_user)], propose: ProposeCreate):
    await db.add_propose(propose.title, propose.status.value, current_user["id"])
    return BasePropose(title=propose.title, status=propose.status.value, created_at=datetime.utcnow().date())


@router.get('/', response_model=List[Propose])
async def get_propose_list(limit: int, page: int) -> List[Propose]:
    response = await db.select_count_propose(limit, page)
    return response


@router.get('/{propose_id}', response_model=Propose)
async def get_propose(current_user: Annotated[User, Depends(get_current_user)], propose_id: int):
    response = await db.select_propose(propose_id)
    return response


@router.get('/{propose_id}/responses', response_model=List[Response])
async def get_responses(current_user: Annotated[User, Depends(get_current_user)], propose_id: int):
    response = await db.get_responses(propose_id, current_user["id"])
    return response


@router.post('/{propose_id}', response_model=List[Response], status_code=201)
async def send_response(current_user: Annotated[User, Depends(get_current_user)], propose_id: int,
                        response: BaseResponse):
    await db.add_response(response.text, current_user["id"], propose_id)
    response = await db.get_responses(propose_id, current_user["id"])
    return response


@router.post('/chat/{response_id}', response_model=List[Dialog], status_code=201)
async def send_message(current_user: Annotated[User, Depends(get_current_user)],
                       propose_id: int, response_id: int, message: BaseResponse
                       ):
    await db.add_message(message.text, response_id, current_user["id"])
    response = await db.get_dialog_history(response_id)
    return response
