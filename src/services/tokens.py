import jwt
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.settings import settings
from src.models import Seller

class TokenService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def check_password_and_email(self, email: str, password: str) -> int | None:
        query = select(Seller.id).where(
            Seller.email == email,
            Seller.password == password,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    def create_access_token(self, seller_id: int) -> str:
        payload = {
            "sub": str(seller_id),
            "exp": datetime.now(timezone.utc) + timedelta(hours=2),
        }
        return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

    def decode_token(self, token: str) -> int:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        seller_id = payload.get("sub")
        if seller_id is None:
            raise ValueError("Token has no subject")
        return int(seller_id)