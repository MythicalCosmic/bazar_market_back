from typing import Sequence
from datetime import datetime, timezone

from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload

from src.db.models.catalog import Category, Product, ProductImage, Banner
from src.repositories.base import SoftDeleteRepository, BaseRepository


class CategoryRepository(SoftDeleteRepository[Category]):
    model = Category

    async def get_root_categories(self) -> Sequence[Category]:
        stmt = (
            select(Category)
            .where(Category.parent_id.is_(None), Category.deleted_at.is_(None), Category.is_active.is_(True))
            .order_by(Category.sort_order)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_children(self, parent_id: int) -> Sequence[Category]:
        stmt = (
            select(Category)
            .where(Category.parent_id == parent_id, Category.deleted_at.is_(None), Category.is_active.is_(True))
            .order_by(Category.sort_order)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_with_products(self, category_id: int) -> Category | None:
        stmt = (
            select(Category)
            .options(selectinload(Category.products))
            .where(Category.id == category_id, Category.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class ProductRepository(SoftDeleteRepository[Product]):
    model = Product

    async def get_by_category(self, category_id: int, *, offset: int = 0, limit: int = 100) -> Sequence[Product]:
        stmt = (
            select(Product)
            .where(Product.category_id == category_id, Product.deleted_at.is_(None), Product.is_active.is_(True))
            .order_by(Product.sort_order)
            .offset(offset).limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_available(self, *, offset: int = 0, limit: int = 100) -> Sequence[Product]:
        stmt = (
            select(Product)
            .where(Product.is_active.is_(True), Product.in_stock.is_(True), Product.deleted_at.is_(None))
            .order_by(Product.sort_order)
            .offset(offset).limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_on_sale(self, *, offset: int = 0, limit: int = 100) -> Sequence[Product]:
        stmt = (
            select(Product)
            .where(
                Product.discount_price.is_not(None),
                Product.is_active.is_(True),
                Product.deleted_at.is_(None),
            )
            .order_by(Product.sort_order)
            .offset(offset).limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def search(self, query: str, *, offset: int = 0, limit: int = 50) -> Sequence[Product]:
        pattern = f"%{query}%"
        stmt = (
            select(Product)
            .where(
                Product.deleted_at.is_(None),
                Product.is_active.is_(True),
                (Product.name_uz.ilike(pattern) | Product.name_ru.ilike(pattern)),
            )
            .offset(offset).limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def set_stock(self, product_id: int, *, in_stock: bool, stock_qty: float | None = None) -> bool:
        values: dict = {"in_stock": in_stock}
        if stock_qty is not None:
            values["stock_qty"] = stock_qty
        stmt = update(Product).where(Product.id == product_id).values(**values)
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0


class ProductImageRepository(BaseRepository[ProductImage]):
    model = ProductImage

    async def get_by_product(self, product_id: int) -> Sequence[ProductImage]:
        stmt = select(ProductImage).where(ProductImage.product_id == product_id).order_by(ProductImage.sort_order)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def set_primary(self, product_id: int, image_id: int) -> None:
        await self.session.execute(
            update(ProductImage).where(ProductImage.product_id == product_id).values(is_primary=False)
        )
        await self.session.execute(
            update(ProductImage).where(ProductImage.id == image_id, ProductImage.product_id == product_id).values(is_primary=True)
        )
        await self.session.flush()


class BannerRepository(BaseRepository[Banner]):
    model = Banner

    async def get_active(self) -> Sequence[Banner]:
        now = func.now()
        stmt = (
            select(Banner)
            .where(
                Banner.is_active.is_(True),
                (Banner.starts_at.is_(None) | (Banner.starts_at <= now)),
                (Banner.expires_at.is_(None) | (Banner.expires_at >= now)),
            )
            .order_by(Banner.sort_order)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
