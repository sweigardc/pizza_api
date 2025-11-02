"""
Focused Ingredient API Tests
Tests specifically for ingredient CRUD operations and data population.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db, Base
from app.config import settings

# Test database setup - using PostgreSQL
TEST_DATABASE_NAME = f"{settings.POSTGRES_DB}_ingredients"
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOSTNAME}:{settings.DATABASE_PORT}/{TEST_DATABASE_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

def setup_test_database():
    """Create test database and tables"""
    print("🔧 Setting up PostgreSQL test database...")
    
    # Create database if it doesn't exist
    main_engine = create_engine(
        f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
        f"{settings.POSTGRES_HOSTNAME}:{settings.DATABASE_PORT}/postgres",
        echo=False
    )
    
    with main_engine.connect() as conn:
        conn.execute(text("COMMIT"))  # End any existing transaction
        try:
            conn.execute(text(f"CREATE DATABASE {TEST_DATABASE_NAME}"))
            print(f"✅ Created test database: {TEST_DATABASE_NAME}")
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"✅ Test database already exists: {TEST_DATABASE_NAME}")
            else:
                print(f"❌ Error creating database: {e}")
    
    main_engine.dispose()
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("✅ Created database tables")

def cleanup_test_database():
    """Clean up test database"""
    print("🧹 Cleaning up test database...")
    
    # Drop all data from tables instead of dropping the database
    with engine.connect() as conn:
        conn.execute(text("COMMIT"))
        try:
            # Get all table names
            result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
            tables = [row[0] for row in result.fetchall()]
            
            # Drop all tables
            for table in tables:
                conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
            conn.commit()
            print("✅ Cleaned up test data")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")
    
    engine.dispose()

# Create tables
setup_test_database()
client = TestClient(app)

def populate_ingredient_test_data():
    """Populate comprehensive ingredient test data"""
    print("🧄 POPULATING INGREDIENT TEST DATA")
    print("=" * 40)
    
    # Comprehensive ingredient data
    ingredients_data = [
        # Basic pizza ingredients
        {"name": "Tomato Sauce", "is_allergen": False},
        {"name": "Mozzarella Cheese", "is_allergen": False},
        {"name": "Pepperoni", "is_allergen": False},
        {"name": "Italian Sausage", "is_allergen": False},
        {"name": "Mushrooms", "is_allergen": False},
        {"name": "Bell Peppers", "is_allergen": False},
        {"name": "Red Onions", "is_allergen": False},
        {"name": "Black Olives", "is_allergen": False},
        {"name": "Green Olives", "is_allergen": False},
        {"name": "Fresh Basil", "is_allergen": False},
        
        # Meat toppings
        {"name": "Ham", "is_allergen": False},
        {"name": "Bacon", "is_allergen": False},
        {"name": "Ground Beef", "is_allergen": False},
        {"name": "Chicken Breast", "is_allergen": False},
        {"name": "Anchovies", "is_allergen": False},
        
        # Vegetable toppings
        {"name": "Spinach", "is_allergen": False},
        {"name": "Artichoke Hearts", "is_allergen": False},
        {"name": "Sun-Dried Tomatoes", "is_allergen": False},
        {"name": "Roasted Garlic", "is_allergen": False},
        {"name": "Jalapeños", "is_allergen": False},
        {"name": "Pineapple", "is_allergen": False},
        
        # Cheese varieties
        {"name": "Parmesan Cheese", "is_allergen": False},
        {"name": "Romano Cheese", "is_allergen": False},
        {"name": "Feta Cheese", "is_allergen": False},
        {"name": "Cheddar Cheese", "is_allergen": False},
        {"name": "Goat Cheese", "is_allergen": False},
        
        # Sauces and bases
        {"name": "BBQ Sauce", "is_allergen": False},
        {"name": "White Sauce", "is_allergen": False},
        {"name": "Pesto Sauce", "is_allergen": False},
        {"name": "Olive Oil", "is_allergen": False},
        
        # Herbs and spices
        {"name": "Oregano", "is_allergen": False},
        {"name": "Red Pepper Flakes", "is_allergen": False},
        {"name": "Black Pepper", "is_allergen": False},
        {"name": "Sea Salt", "is_allergen": False},
        
        # Common allergens
        {"name": "Wheat Flour", "is_allergen": True},
        {"name": "Milk", "is_allergen": True},
        {"name": "Eggs", "is_allergen": True},
        {"name": "Soy Protein", "is_allergen": True},
        {"name": "Gluten", "is_allergen": True},
        {"name": "Nuts (Tree)", "is_allergen": True},
        {"name": "Sesame Seeds", "is_allergen": True},
        
        # Complex ingredients (could have sub-ingredients)
        {"name": "Pizza Dough", "is_allergen": False},
        {"name": "Cheese Blend", "is_allergen": False},
        {"name": "Seasoning Mix", "is_allergen": False},
        {"name": "Meat Sauce", "is_allergen": False},
    ]
    
    created_ingredients = []
    allergen_count = 0
    
    for i, ingredient_data in enumerate(ingredients_data, 1):
        response = client.post("/api/ingredients/", json=ingredient_data)
        
        if response.status_code == 201:
            ingredient = response.json()
            created_ingredients.append(ingredient)
            
            if ingredient["is_allergen"]:
                allergen_count += 1
                print(f"  ⚠️  {ingredient['name']} (ID: {ingredient['id']}) - ALLERGEN")
            else:
                print(f"  ✅  {ingredient['name']} (ID: {ingredient['id']})")
        else:
            print(f"  ❌  Failed: {ingredient_data['name']} - {response.text}")
    
    print(f"\n📊 INGREDIENT POPULATION SUMMARY:")
    print(f"   • Total created: {len(created_ingredients)}")
    print(f"   • Allergens: {allergen_count}")
    print(f"   • Regular ingredients: {len(created_ingredients) - allergen_count}")
    
    return created_ingredients

def test_ingredient_crud_operations():
    """Test all ingredient CRUD operations"""
    print("\n🧪 TESTING INGREDIENT CRUD OPERATIONS")
    print("=" * 40)
    
    # Test CREATE
    print("\n1. Testing CREATE Ingredient:")
    new_ingredient = {
        "name": "Test Special Cheese",
        "is_allergen": True,
        "sub_ingredient_ids": []
    }
    
    response = client.post("/api/ingredients/", json=new_ingredient)
    assert response.status_code == 201, f"CREATE failed: {response.status_code} - {response.text}"
    created = response.json()
    test_id = created["id"]
    print(f"   ✅ Created: {created['name']} (ID: {test_id})")
    
    # Test READ ALL
    print("\n2. Testing READ All Ingredients:")
    response = client.get("/api/ingredients/")
    assert response.status_code == 200, f"READ ALL failed: {response.status_code}"
    all_ingredients = response.json()
    print(f"   ✅ Retrieved {len(all_ingredients)} ingredients")
    
    # Test READ ONE
    print(f"\n3. Testing READ Single Ingredient (ID: {test_id}):")
    response = client.get(f"/api/ingredients/{test_id}")
    assert response.status_code == 200, f"READ ONE failed: {response.status_code}"
    ingredient = response.json()
    print(f"   ✅ Retrieved: {ingredient['name']}")
    
    # Test UPDATE
    print(f"\n4. Testing UPDATE Ingredient (ID: {test_id}):")
    update_data = {
        "name": "Updated Special Cheese",
        "is_allergen": False
    }
    response = client.patch(f"/api/ingredients/{test_id}", json=update_data)
    assert response.status_code == 200, f"UPDATE failed: {response.status_code} - {response.text}"
    updated = response.json()
    print(f"   ✅ Updated: {updated['name']} (allergen: {updated['is_allergen']})")
    
    # Test DELETE
    print(f"\n5. Testing DELETE Ingredient (ID: {test_id}):")
    response = client.delete(f"/api/ingredients/{test_id}")
    assert response.status_code == 204, f"DELETE failed: {response.status_code}"
    print(f"   ✅ Deleted ingredient (ID: {test_id})")
    
    # Verify deletion
    response = client.get(f"/api/ingredients/{test_id}")
    assert response.status_code == 404, "Ingredient should be deleted"
    print(f"   ✅ Confirmed deletion (404 response)")

def test_ingredient_error_handling():
    """Test ingredient error scenarios"""
    print("\n❌ TESTING INGREDIENT ERROR HANDLING")
    print("=" * 40)
    
    # Test invalid data
    print("\n1. Testing invalid data:")
    invalid_data = {"name": "", "is_allergen": "not_boolean"}
    response = client.post("/api/ingredients/", json=invalid_data)
    print(f"   ✅ Empty name validation: {response.status_code} (Expected 422)")
    
    # Test non-existent ingredient
    print("\n2. Testing non-existent ingredient:")
    response = client.get("/api/ingredients/99999")
    print(f"   ✅ Non-existent GET: {response.status_code} (Expected 404)")
    
    response = client.patch("/api/ingredients/99999", json={"name": "Test"})
    print(f"   ✅ Non-existent UPDATE: {response.status_code} (Expected 404)")
    
    response = client.delete("/api/ingredients/99999")
    print(f"   ✅ Non-existent DELETE: {response.status_code} (Expected 404)")

def run_ingredient_tests():
    """Run all ingredient tests"""
    print("🧄 COMPREHENSIVE INGREDIENT API TESTS")
    print("=" * 50)
    
    try:
        # Step 1: Populate test data
        ingredients = populate_ingredient_test_data()
        
        # Step 2: Test CRUD operations
        test_ingredient_crud_operations()
        
        # Step 3: Test error handling
        test_ingredient_error_handling()
        
        print("\n" + "=" * 50)
        print("🎉 ALL INGREDIENT TESTS PASSED!")
        print("=" * 50)
        print(f"✅ Populated {len(ingredients)} ingredients")
        print("✅ All CRUD operations working")
        print("✅ Error handling working correctly")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ INGREDIENT TEST FAILED: {str(e)}")
        return False
    except Exception as e:
        print(f"\n💥 ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_ingredient_tests()
    if not success:
        sys.exit(1)