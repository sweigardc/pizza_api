from . import schemas, models
from sqlalchemy.orm import Session, joinedload
from fastapi import Depends, HTTPException, status, APIRouter, Response, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_, func
from typing import List, Optional
from .database import get_db

router = APIRouter()

def _get_all_allergens_for_pizza(pizza: models.Pizza) -> List[models.Ingredient]:
    """Get all potential allergens for a pizza, including sub-ingredients"""
    allergens = set()
    
    for ingredient in pizza.ingredients:
        # Check if the ingredient itself is an allergen
        if ingredient.is_allergen:
            allergens.add(ingredient)
        
        # Check sub-ingredients recursively
        def check_sub_ingredients(ing):
            for sub_ing in ing.sub_ingredients:
                if sub_ing.is_allergen:
                    allergens.add(sub_ing)
                check_sub_ingredients(sub_ing)  # Recursive check
        
        check_sub_ingredients(ingredient)
    
    return list(allergens)

@router.get('/', response_model=schemas.PizzaListResponse)
def get_pizzas(
    db: Session = Depends(get_db), 
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    search: str = Query('', description="Search pizzas by name or description"),
    sort_by_name: bool = Query(False, description="Sort pizzas alphabetically by name"),
    ingredient_filter: Optional[str] = Query(None, description="Filter by ingredient name"),
    allergen_filter: Optional[str] = Query(None, description="Filter by allergen name"),
    has_allergens: Optional[bool] = Query(None, description="Filter pizzas that have/don't have allergens")
):
    """
    Get pizzas with advanced filtering and sorting options:
    - Search by keyword in name or description
    - Sort by name alphabetically
    - Filter by direct ingredients
    - Filter by allergens (including sub-ingredients)
    """
    skip = (page - 1) * limit
    
    # Start with base query
    query = db.query(models.Pizza).options(
        joinedload(models.Pizza.ingredients).joinedload(models.Ingredient.sub_ingredients)
    )
    
    # Search filter
    if search:
        query = query.filter(
            or_(
                models.Pizza.name.icontains(search),
                models.Pizza.description.icontains(search)
            )
        )
    
    # Ingredient filter - direct ingredients only
    if ingredient_filter:
        query = query.join(models.Pizza.ingredients).filter(
            models.Ingredient.name.icontains(ingredient_filter)
        )
    
    # Allergen filter - includes sub-ingredients
    if allergen_filter:
        # This is more complex as we need to check sub-ingredients too
        # We'll filter in Python after fetching to handle recursive allergen checking
        pass
    
    # Sort by name if requested
    if sort_by_name:
        query = query.order_by(models.Pizza.name.asc())
    else:
        query = query.order_by(models.Pizza.created_at.desc())
    
    # Get total count before pagination
    total_count = query.count()
    
    # Apply pagination
    pizzas = query.offset(skip).limit(limit).all()
    
    # Process each pizza to add allergen information and apply allergen filtering
    processed_pizzas = []
    for pizza in pizzas:
        # Get all allergens for this pizza
        pizza_allergens = _get_all_allergens_for_pizza(pizza)
        
        # Apply allergen filter if specified
        if allergen_filter:
            allergen_names = [allergen.name.lower() for allergen in pizza_allergens]
            if not any(allergen_filter.lower() in name for name in allergen_names):
                continue
        
        # Apply has_allergens filter if specified
        if has_allergens is not None:
            if has_allergens and not pizza_allergens:
                continue
            elif not has_allergens and pizza_allergens:
                continue
        
        # Add allergen information to pizza for response
        pizza.potential_allergens = pizza_allergens
        processed_pizzas.append(pizza)
    
    return schemas.PizzaListResponse(
        status="success",
        results=len(processed_pizzas),
        pizzas=processed_pizzas
    )

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.PizzaDetailResponse)
def create_pizza(payload: schemas.PizzaCreate, db: Session = Depends(get_db)):
    """Create a new pizza with specified ingredients"""
    
    # Verify all ingredient IDs exist
    if payload.ingredient_ids:
        ingredients = db.query(models.Ingredient).filter(
            models.Ingredient.id.in_(payload.ingredient_ids)
        ).all()
        
        if len(ingredients) != len(payload.ingredient_ids):
            found_ids = [ing.id for ing in ingredients]
            missing_ids = set(payload.ingredient_ids) - set(found_ids)
            raise HTTPException(
                status_code=400, 
                detail=f"Ingredients with IDs {list(missing_ids)} not found"
            )
    else:
        ingredients = []
    
    new_pizza = models.Pizza(
        name=payload.name,
        description=payload.description,
        ingredients=ingredients
    )

    db.add(new_pizza)
    try:
        db.commit()
        db.refresh(new_pizza)
        # Add allergen information
        new_pizza.potential_allergens = _get_all_allergens_for_pizza(new_pizza)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Pizza with this name already exists.")

    return schemas.PizzaDetailResponse(status="success", pizza=new_pizza)

@router.patch('/{pizza_id}', response_model=schemas.PizzaDetailResponse)
def update_pizza(pizza_id: int, payload: schemas.PizzaUpdate, db: Session = Depends(get_db)):
    """Update an existing pizza"""
    
    pizza = db.query(models.Pizza).options(
        joinedload(models.Pizza.ingredients).joinedload(models.Ingredient.sub_ingredients)
    ).filter(models.Pizza.id == pizza_id).first()
    
    if not pizza:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No pizza with this id: {pizza_id} found'
        )

    # Update basic fields
    if payload.name is not None:
        pizza.name = payload.name
    if payload.description is not None:
        pizza.description = payload.description
    
    # Update ingredients if provided
    if payload.ingredient_ids is not None:
        ingredients = db.query(models.Ingredient).filter(
            models.Ingredient.id.in_(payload.ingredient_ids)
        ).all()
        
        if len(ingredients) != len(payload.ingredient_ids):
            found_ids = [ing.id for ing in ingredients]
            missing_ids = set(payload.ingredient_ids) - set(found_ids)
            raise HTTPException(
                status_code=400, 
                detail=f"Ingredients with IDs {list(missing_ids)} not found"
            )
        
        pizza.ingredients = ingredients

    try:
        db.commit()
        db.refresh(pizza)
        # Add allergen information
        pizza.potential_allergens = _get_all_allergens_for_pizza(pizza)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Pizza name already exists.")
    
    return schemas.PizzaDetailResponse(status="success", pizza=pizza)

@router.get('/{pizza_id}', response_model=schemas.PizzaDetailResponse)
def get_pizza(pizza_id: int, db: Session = Depends(get_db)):
    """Get a specific pizza by ID with all ingredient and allergen information"""
    
    pizza = db.query(models.Pizza).options(
        joinedload(models.Pizza.ingredients).joinedload(models.Ingredient.sub_ingredients)
    ).filter(models.Pizza.id == pizza_id).first()
    
    if not pizza:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No pizza with this id: {pizza_id} found"
        )
    
    # Add allergen information
    pizza.potential_allergens = _get_all_allergens_for_pizza(pizza)
    
    return schemas.PizzaDetailResponse(status="success", pizza=pizza)

@router.delete('/{pizza_id}')
def delete_pizza(pizza_id: int, db: Session = Depends(get_db)):
    """Delete a pizza"""
    
    pizza = db.query(models.Pizza).filter(models.Pizza.id == pizza_id).first()
    if not pizza:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No pizza with this id: {pizza_id} found'
        )
    
    db.delete(pizza)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Additional endpoint to get all available ingredients
@router.get('/ingredients/', response_model=List[schemas.IngredientResponse])
def get_ingredients(db: Session = Depends(get_db)):
    """Get all available ingredients"""
    ingredients = db.query(models.Ingredient).options(
        joinedload(models.Ingredient.sub_ingredients)
    ).all()
    return ingredients
