from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Boolean, Integer, Text, Numeric, ForeignKey, Index, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base import Base, TimestampMixin, SoftDeleteMixin, UUIDMixin


class Category(UUIDMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"))
    name_uz: Mapped[str] = mapped_column(String(200), nullable=False)
    name_ru: Mapped[str | None] = mapped_column(String(200))
    image: Mapped[str | None] = mapped_column(String(500))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    parent: Mapped["Category | None"] = relationship(remote_side="Category.id", lazy="joined")
    children: Mapped[list["Category"]] = relationship(back_populates="parent", lazy="selectin")
    products: Mapped[list["Product"]] = relationship(back_populates="category", lazy="noload")

    __table_args__ = (
        Index("idx_categories_parent", "parent_id"),
        Index("idx_categories_sort", "sort_order"),
        Index("idx_categories_active", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<Category {self.id} {self.name_uz}>"


class Product(UUIDMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    name_uz: Mapped[str] = mapped_column(String(300), nullable=False)
    name_ru: Mapped[str | None] = mapped_column(String(300))
    description_uz: Mapped[str | None] = mapped_column(Text)
    description_ru: Mapped[str | None] = mapped_column(Text)

    unit: Mapped[str] = mapped_column(String(20), nullable=False) 
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    discount_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    step: Mapped[Decimal] = mapped_column(Numeric(8, 3), default=Decimal("1"))
    min_qty: Mapped[Decimal] = mapped_column(Numeric(8, 3), default=Decimal("1"))
    max_qty: Mapped[Decimal | None] = mapped_column(Numeric(8, 3))

    in_stock: Mapped[bool] = mapped_column(Boolean, default=True)
    stock_qty: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))

    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    category: Mapped["Category"] = relationship(back_populates="products", lazy="joined")
    images: Mapped[list["ProductImage"]] = relationship(
        back_populates="product", lazy="selectin", order_by="ProductImage.sort_order"
    )

    __table_args__ = (
        Index("idx_products_category", "category_id"),
        Index("idx_products_active", "is_active"),
        Index("idx_products_available", "is_active", "in_stock"),
        Index("idx_products_category_sort", "category_id", "sort_order"),
    )

    @property
    def primary_image(self) -> str | None:
        for img in self.images:
            if img.is_primary:
                return img.image
        return self.images[0].image if self.images else None

    def __repr__(self) -> str:
        return f"<Product {self.id} {self.name_uz} ({self.price} / {self.unit})>"


class ProductImage(Base):
    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    image: Mapped[str] = mapped_column(String(500), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)

    product: Mapped["Product"] = relationship(back_populates="images")

    __table_args__ = (
        Index("idx_product_images_product_sort", "product_id", "sort_order"),
    )


class Banner(TimestampMixin, Base):
    __tablename__ = "banners"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str | None] = mapped_column(String(200))
    image: Mapped[str] = mapped_column(String(500), nullable=False)
    link_type: Mapped[str | None] = mapped_column(String(30))  
    link_value: Mapped[str | None] = mapped_column(String(500))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    starts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (
        Index("idx_banners_active", "is_active", "starts_at", "expires_at"),
    )