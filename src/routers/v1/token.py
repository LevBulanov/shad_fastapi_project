from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.schemas import CreateToken, ReturnToken
from src.services import TokenService

token_router = APIRouter(prefix="/token", tags=["JWT"])

DBSession = Annotated[AsyncSession, Depends(get_async_session)]

@token_router.post(
    "/",
    response_model=ReturnToken,
    responses={401: {"description": "Invalid credentials"}},
)
async def create_token(token_data: CreateToken, session: DBSession):
    seller_id = await TokenService(session).check_password_and_email(
        token_data.email,
        token_data.password,
    )

    if seller_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    new_token = TokenService(session).create_access_token(seller_id)

    return ReturnToken(access_token=new_token)