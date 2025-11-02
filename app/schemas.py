from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

# Ingredient schemas
class IngredientBase(BaseModel):
    name: str
    is_allergen: bool = False

class IngredientCreate(IngredientBase):
    sub_ingredient_ids: Optional[List[int]] = []

class IngredientUpdate(BaseModel):
    name: Optional[str] = None
    is_allergen: Optional[bool] = None
    sub_ingredient_ids: Optional[List[int]] = None

class IngredientResponse(IngredientBase):
    id: int
    sub_ingredients: List["IngredientResponse"] = []
    
    class Config:
        from_attributes = True

# Pizza schemas
class PizzaBase(BaseModel):
    name: str
    description: str

class PizzaCreate(PizzaBase):
    ingredient_ids: List[int] = []

class PizzaUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    ingredient_ids: Optional[List[int]] = None

class PizzaResponse(PizzaBase):
    id: int
    created_at: datetime
    updated_at: datetime
    ingredients: List[IngredientResponse] = []
    potential_allergens: List[IngredientResponse] = []
    
    class Config:
        from_attributes = True

class PizzaListResponse(BaseModel):
    status: str
    results: int
    pizzas: List[PizzaResponse]

class PizzaDetailResponse(BaseModel):
    status: str
    pizza: PizzaResponse

