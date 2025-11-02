from app import models, pizza, ingredients
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.database import get_db, initialize_database
from dotenv import load_dotenv
import os
import requests
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

load_dotenv()

app = FastAPI()

# Initialize database tables
initialize_database()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pizza.router, tags=['Pizzas'], prefix='/api/pizzas')
app.include_router(ingredients.router, tags=['Ingredients'], prefix='/api/ingredients')

@app.get("/")
async def root():
    return {"message": "Welcome to Pizza API. See /docs for API documentation."}

@app.get("/api/healthchecker")
def root():
    return {"message": "Welcome to Pizza API. See /docs for API documentation."}

@app.get("/api/db-healthchecker")
def db_healthchecker(db: Session = Depends(get_db)):
    try:
        # Attempt to execute a simple query to check database connectivity
        from app.database import engine
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
        return {"message": "Database is healthy"}
    except OperationalError:
        raise HTTPException(status_code=500, detail="Database is not reachable")    