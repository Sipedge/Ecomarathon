from fastapi import APIRouter, Form, Response, HTTPException, status
from ..data import Lobby, DICT_LOBBY, USERNAMES
from typing import Annotated

router = APIRouter(tags=["Пользователи"])

@router.post('/create')
async def add_user(username: Annotated[str, Form()]):
    if username in USERNAMES:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)
    USERNAMES.add(username)
    return {"username" : username}

@router.head('/ping')
async def ping(response: Response):
    response.headers["X-Ping"] = "Connect"
    

