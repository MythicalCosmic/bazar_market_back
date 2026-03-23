from decimal import Decimal
from typing import Sequence

from sqlalchemy import select, update, delete

from src.db.models.cart import CartItem
from src.repositories.base import BaseRepository


class CartRepository(BaseRepository[CartItem]):
    model = CartItem

    async def get_by_user(self, user_id: int) -> Sequence[CartItem]:
        stmt = select(CartItem).where(CartItem.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_item(self, user_id: int, product_id: int) -> CartItem | None:
        stmt = select(CartItem).where(CartItem.user_id == user_id, CartItem.product_id == product_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert(self, user_id: int, product_id: int, quantity: Decimal) -> CartItem:
        existing = await self.get_item(user_id, product_id)
        if existing:
            existing.quantity = quantity
            await self.session.flush()
            return existing
        return await self.create(user_id=user_id, product_id=product_id, quantity=quantity)

    async def remove_item(self, user_id: int, product_id: int) -> bool:
        stmt = delete(CartItem).where(CartItem.user_id == user_id, CartItem.product_id == product_id)
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0

    async def clear(self, user_id: int) -> int:
        stmt = delete(CartItem).where(CartItem.user_id == user_id)
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount
