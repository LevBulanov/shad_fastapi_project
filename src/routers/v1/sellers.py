from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.models import Seller
from src.schemas import ReadSeller, ReadAllSellers, ReadSellerAndBooks, CreateSeller, UpdateSeller
from src.services import SellerServices
from src.dependency.dependencies import get_current_seller

DBSession = Annotated[AsyncSession, Depends(get_async_session)]

sellers_router = APIRouter(prefix="/seller", tags=["Sellers"])


@sellers_router.post("/", response_model=ReadSeller, status_code=status.HTTP_201_CREATED)
async def create_seller(session: DBSession, seller: CreateSeller):
    seller = await SellerServices(session).add_seller(seller)

    return seller


@sellers_router.get("/", response_model=ReadAllSellers)
async def get_all_sellers(session: DBSession):
    sellers = await SellerServices(session).get_all_sellers()

    return {"sellers": sellers}


@sellers_router.get("/{seller_id}", response_model=ReadSellerAndBooks)
async def get_all_sellers_and_books(session: DBSession, seller: Seller = Depends(get_current_seller)):
    seller = await SellerServices(session).get_single_seller(seller.id)
    return seller 


@sellers_router.put('/{seller_id}', response_model=ReadSeller)
async def update_seller(session: DBSession, seller_id: int, new_seller_data: UpdateSeller):
    new_seller = await SellerServices(session).update_seller(seller_id, new_seller_data)
    
    if not new_seller:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    return new_seller


@sellers_router.delete('/{seller_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_seller_and_books(session: DBSession, seller_id: int):
    deleted_book = await SellerServices(session).delete_seller(seller_id)

    if not deleted_book:
        return Response(status_code=status.HTTP_404_NOT_FOUND)