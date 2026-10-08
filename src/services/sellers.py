from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Seller
from src.schemas.sellers import CreateSeller, UpdateSeller



class SellerServices:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_seller(self, seller: CreateSeller) -> Seller:
        new_seller = Seller(first_name=seller.first_name,
                            last_name=seller.last_name,
                            email=seller.email,
                            password=seller.password)
        
        self.session.add(new_seller)
        await self.session.flush()

        
        return new_seller
    

    async def delete_seller(self, seller_id: int) -> bool:
        seller = await self.session.get(Seller, seller_id)

        if seller:
            await self.session.delete(seller)
            return seller
        
        else:
            return False
        
    
    async def update_seller(self, seller_id: int, new_seller_data: UpdateSeller) -> Seller | None:
        if updated_seller := await self.session.get(Seller, seller_id):
            updated_seller.first_name = new_seller_data.first_name
            updated_seller.last_name = new_seller_data.last_name
            updated_seller.email = new_seller_data.email

            await self.session.flush()

            return updated_seller 
        

    async def get_single_seller(self, seller_id: int) -> Seller | None:
        return await self.session.get(Seller, seller_id) 
    

    async def get_all_sellers(self) -> list[Seller]:
        query = select(Seller)

        result = await self.session.execute(query)

        return result.scalars().all()
        
    

        

