from app.database import Base
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship

# Association table for ingredient self-referential relationship
ingredient_ingredients = Table(
    'ingredient_ingredients',
    Base.metadata,
    Column('parent_ingredient_id', Integer, ForeignKey('ingredients.id')),
    Column('child_ingredient_id', Integer, ForeignKey('ingredients.id'))
)

# Association table for pizza-ingredient many-to-many relationship
pizza_ingredients = Table(
    'pizza_ingredients',
    Base.metadata,
    Column('pizza_id', Integer, ForeignKey('pizzas.id')),
    Column('ingredient_id', Integer, ForeignKey('ingredients.id'))
)

class Ingredient(Base):
    __tablename__ = 'ingredients'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    is_allergen = Column(Boolean, default=False)
    sub_ingredients = relationship(
        "Ingredient",
        secondary=ingredient_ingredients,
        primaryjoin=id == ingredient_ingredients.c.parent_ingredient_id,
        secondaryjoin=id == ingredient_ingredients.c.child_ingredient_id,
        back_populates="parent_ingredients"
    )
    parent_ingredients = relationship(
        "Ingredient",
        secondary=ingredient_ingredients,
        primaryjoin=id == ingredient_ingredients.c.child_ingredient_id,
        secondaryjoin=id == ingredient_ingredients.c.parent_ingredient_id,
        back_populates="sub_ingredients"
    )

class Pizza(Base):
    __tablename__ = 'pizzas'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    ingredients = relationship("Ingredient", secondary=pizza_ingredients)
