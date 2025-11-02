from . import schemas, models
from sqlalchemy.orm import Session, joinedload
from fastapi import Depends, HTTPException, status, APIRouter, Response
from sqlalchemy.exc import IntegrityError
from typing import List
from .database import get_db

router = APIRouter()

@router.get('/', response_model=List[schemas.IngredientResponse])
def get_ingredients(db: Session = Depends(get_db)):
    """Get all ingredients with their sub-ingredients"""
    ingredients = db.query(models.Ingredient).options(
        joinedload(models.Ingredient.sub_ingredients)
    ).all()
    return ingredients

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.IngredientResponse)
def create_ingredient(payload: schemas.IngredientCreate, db: Session = Depends(get_db)):
    """Create a new ingredient with optional sub-ingredients"""
    
    # Verify sub-ingredient IDs exist if provided
    sub_ingredients = []
    if payload.sub_ingredient_ids:
        sub_ingredients = db.query(models.Ingredient).filter(
            models.Ingredient.id.in_(payload.sub_ingredient_ids)
        ).all()
        
        if len(sub_ingredients) != len(payload.sub_ingredient_ids):
            found_ids = [ing.id for ing in sub_ingredients]
            missing_ids = set(payload.sub_ingredient_ids) - set(found_ids)
            raise HTTPException(
                status_code=400, 
                detail=f"Sub-ingredients with IDs {list(missing_ids)} not found"
            )
    
    new_ingredient = models.Ingredient(
        name=payload.name,
        is_allergen=payload.is_allergen,
        sub_ingredients=sub_ingredients
    )

    db.add(new_ingredient)
    try:
        db.commit()
        db.refresh(new_ingredient)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Ingredient with this name already exists.")

    return new_ingredient

@router.patch('/{ingredient_id}', response_model=schemas.IngredientResponse)
def update_ingredient(ingredient_id: int, payload: schemas.IngredientUpdate, db: Session = Depends(get_db)):
    """Update an existing ingredient"""
    
    ingredient = db.query(models.Ingredient).options(
        joinedload(models.Ingredient.sub_ingredients)
    ).filter(models.Ingredient.id == ingredient_id).first()
    
    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No ingredient with this id: {ingredient_id} found'
        )

    # Update basic fields
    if payload.name is not None:
        ingredient.name = payload.name
    if payload.is_allergen is not None:
        ingredient.is_allergen = payload.is_allergen
    
    # Update sub-ingredients if provided
    if payload.sub_ingredient_ids is not None:
        sub_ingredients = db.query(models.Ingredient).filter(
            models.Ingredient.id.in_(payload.sub_ingredient_ids)
        ).all()
        
        if len(sub_ingredients) != len(payload.sub_ingredient_ids):
            found_ids = [ing.id for ing in sub_ingredients]
            missing_ids = set(payload.sub_ingredient_ids) - set(found_ids)
            raise HTTPException(
                status_code=400, 
                detail=f"Sub-ingredients with IDs {list(missing_ids)} not found"
            )
        
        ingredient.sub_ingredients = sub_ingredients

    try:
        db.commit()
        db.refresh(ingredient)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Ingredient name already exists.")
    
    return ingredient

@router.get('/{ingredient_id}', response_model=schemas.IngredientResponse)
def get_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    """Get a specific ingredient by ID"""
    
    ingredient = db.query(models.Ingredient).options(
        joinedload(models.Ingredient.sub_ingredients)
    ).filter(models.Ingredient.id == ingredient_id).first()
    
    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No ingredient with this id: {ingredient_id} found"
        )
    
    return ingredient

@router.delete('/{ingredient_id}')
def delete_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    """Delete an ingredient"""
    
    ingredient = db.query(models.Ingredient).filter(models.Ingredient.id == ingredient_id).first()
    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No ingredient with this id: {ingredient_id} found'
        )
    
    db.delete(ingredient)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get('/allergens/', response_model=List[schemas.IngredientResponse])
def get_allergens(db: Session = Depends(get_db)):
    """Get all ingredients marked as allergens"""
    allergens = db.query(models.Ingredient).options(
        joinedload(models.Ingredient.sub_ingredients)
    ).filter(models.Ingredient.is_allergen == True).all()
    return allergens