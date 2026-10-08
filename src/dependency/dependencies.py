from typing import Annotated
from jwt import ExpiredSignatureError, InvalidTokenError

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.ext.asyncio import AsyncSession

from src.services.tokens import TokenService
from src.configurations.database import get_async_session
from src.models import Seller

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/token")

DBSession = Annotated[AsyncSession, Depends(get_async_session)]


async def get_current_seller(
    session: DBSession,
    token: str = Depends(oauth2_scheme),
) -> Seller:
    token_service = TokenService(session)

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        seller_id = token_service.decode_token(token)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenError:
        raise credentials_exception

    seller = await session.get(Seller, seller_id)

    if seller is None:
        raise credentials_exception

    return seller