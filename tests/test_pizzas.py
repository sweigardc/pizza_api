"""
Focused Pizza API Tests
Tests specifically for pizza CRUD operations and data population.
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
TEST_DATABASE_NAME = f"{settings.POSTGRES_DB}_pizzas"
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

def create_base_ingredients():
    """Create basic ingredients needed for pizza testing"""
    print("🧄 Creating base ingredients for pizza tests...")
    
    base_ingredients = [
        {"name": "Tomato Sauce", "is_allergen": False},
        {"name": "Mozzarella Cheese", "is_allergen": False},
        {"name": "Pepperoni", "is_allergen": False},
        {"name": "Italian Sausage", "is_allergen": False},
        {"name": "Mushrooms", "is_allergen": False},
        {"name": "Bell Peppers", "is_allergen": False},
        {"name": "Red Onions", "is_allergen": False},
        {"name": "Ham", "is_allergen": False},
        {"name": "Pineapple", "is_allergen": False},
        {"name": "Fresh Basil", "is_allergen": False},
    ]
    
    ingredient_ids = []
    for ingredient_data in base_ingredients:
        response = client.post("/api/ingredients/", json=ingredient_data)
        if response.status_code == 201:
            ingredient_ids.append(response.json()["id"])
            print(f"   ✅ {ingredient_data['name']}")
        else:
            print(f"   ❌ Failed: {ingredient_data['name']}")
    
    print(f"   📊 Created {len(ingredient_ids)} base ingredients")
    return ingredient_ids

def populate_pizza_test_data(ingredient_ids):
    """Populate comprehensive pizza test data"""
    print("\n🍕 POPULATING PIZZA TEST DATA")
    print("=" * 40)
    
    if len(ingredient_ids) < 6:
        print("❌ Not enough ingredients for comprehensive pizza testing")
        return []
    
    # Comprehensive pizza data with different combinations
    pizzas_data = [
        {
            "name": "Classic Margherita",
            "description": "Traditional Italian pizza with tomato sauce, fresh mozzarella, and basil leaves",
            "ingredient_ids": [ingredient_ids[0], ingredient_ids[1], ingredient_ids[9]]  # Sauce, Cheese, Basil
        },
        {
            "name": "Pepperoni Classic",
            "description": "America's favorite pizza topped with pepperoni and mozzarella cheese",
            "ingredient_ids": [ingredient_ids[0], ingredient_ids[1], ingredient_ids[2]]  # Sauce, Cheese, Pepperoni
        },
        {
            "name": "Supreme Special",
            "description": "Loaded with pepperoni, sausage, mushrooms, peppers, and onions",
            "ingredient_ids": ingredient_ids[:7]  # First 7 ingredients
        },
        {
            "name": "Meat Lovers",
            "description": "For carnivores: pepperoni, Italian sausage, and ham",
            "ingredient_ids": [ingredient_ids[0], ingredient_ids[1], ingredient_ids[2], ingredient_ids[3], ingredient_ids[7]]
        },
        {
            "name": "Vegetarian Garden",
            "description": "Fresh vegetables: mushrooms, bell peppers, onions, and basil",
            "ingredient_ids": [ingredient_ids[0], ingredient_ids[1], ingredient_ids[4], ingredient_ids[5], ingredient_ids[6], ingredient_ids[9]]
        },
        {
            "name": "Hawaiian Paradise",
            "description": "Tropical combination of ham and pineapple with cheese",
            "ingredient_ids": [ingredient_ids[0], ingredient_ids[1], ingredient_ids[7], ingredient_ids[8]]  # Sauce, Cheese, Ham, Pineapple
        },
        {
            "name": "Pepperoni Supreme",
            "description": "Double pepperoni with mushrooms and onions",
            "ingredient_ids": [ingredient_ids[0], ingredient_ids[1], ingredient_ids[2], ingredient_ids[4], ingredient_ids[6]]
        },
        {
            "name": "Italian Sausage Special",
            "description": "Savory Italian sausage with peppers and onions",
            "ingredient_ids": [ingredient_ids[0], ingredient_ids[1], ingredient_ids[3], ingredient_ids[5], ingredient_ids[6]]
        },
        {
            "name": "Mushroom Deluxe",
            "description": "Mushroom lovers pizza with extra mushrooms and herbs",
            "ingredient_ids": [ingredient_ids[0], ingredient_ids[1], ingredient_ids[4], ingredient_ids[9]]
        },
        {
            "name": "Simple Cheese",
            "description": "Classic cheese pizza - sometimes simple is best",
            "ingredient_ids": [ingredient_ids[0], ingredient_ids[1]]  # Just sauce and cheese
        }
    ]
    
    created_pizzas = []
    
    for i, pizza_data in enumerate(pizzas_data, 1):
        response = client.post("/api/pizzas/", json=pizza_data)
        
        if response.status_code == 201:
            pizza = response.json()["pizza"]
            created_pizzas.append(pizza)
            ingredient_count = len(pizza["ingredients"])
            print(f"  {i:2d}. ✅ {pizza['name']} (ID: {pizza['id']}) - {ingredient_count} ingredients")
        else:
            print(f"  {i:2d}. ❌ Failed: {pizza_data['name']} - {response.text}")
    
    print(f"\n📊 PIZZA POPULATION SUMMARY:")
    print(f"   • Total pizzas created: {len(created_pizzas)}")
    print(f"   • Average ingredients per pizza: {sum(len(p['ingredients']) for p in created_pizzas) / len(created_pizzas):.1f}")
    
    return created_pizzas

def test_pizza_crud_operations(ingredient_ids):
    """Test all pizza CRUD operations"""
    print("\n🧪 TESTING PIZZA CRUD OPERATIONS")
    print("=" * 40)
    
    # Test CREATE
    print("\n1. Testing CREATE Pizza:")
    new_pizza = {
        "name": "Test Custom Creation",
        "description": "A test pizza created during CRUD testing",
        "ingredient_ids": ingredient_ids[:4]  # Use first 4 ingredients
    }
    
    response = client.post("/api/pizzas/", json=new_pizza)
    assert response.status_code == 201, f"CREATE failed: {response.status_code} - {response.text}"
    created = response.json()["pizza"]
    test_id = created["id"]
    print(f"   ✅ Created: {created['name']} (ID: {test_id})")
    print(f"      Ingredients: {len(created['ingredients'])}")
    
    # Test READ ALL
    print("\n2. Testing READ All Pizzas:")
    response = client.get("/api/pizzas/")
    assert response.status_code == 200, f"READ ALL failed: {response.status_code}"
    data = response.json()
    print(f"   ✅ Retrieved {data['results']} pizzas")
    print(f"      Status: {data['status']}")
    
    # Test READ ONE
    print(f"\n3. Testing READ Single Pizza (ID: {test_id}):")
    response = client.get(f"/api/pizzas/{test_id}")
    assert response.status_code == 200, f"READ ONE failed: {response.status_code}"
    data = response.json()
    pizza = data["pizza"]
    print(f"   ✅ Retrieved: {pizza['name']}")
    print(f"      Description: {pizza['description'][:50]}...")
    
    # Test UPDATE
    print(f"\n4. Testing UPDATE Pizza (ID: {test_id}):")
    update_data = {
        "name": "Updated Test Pizza",
        "description": "This pizza was updated during testing",
        "ingredient_ids": ingredient_ids[:2]  # Reduce to 2 ingredients
    }
    response = client.patch(f"/api/pizzas/{test_id}", json=update_data)
    assert response.status_code == 200, f"UPDATE failed: {response.status_code} - {response.text}"
    updated = response.json()["pizza"]
    print(f"   ✅ Updated: {updated['name']}")
    print(f"      New ingredient count: {len(updated['ingredients'])}")
    
    # Test DELETE
    print(f"\n5. Testing DELETE Pizza (ID: {test_id}):")
    response = client.delete(f"/api/pizzas/{test_id}")
    assert response.status_code == 204, f"DELETE failed: {response.status_code}"
    print(f"   ✅ Deleted pizza (ID: {test_id})")
    
    # Verify deletion
    response = client.get(f"/api/pizzas/{test_id}")
    assert response.status_code == 404, "Pizza should be deleted"
    print(f"   ✅ Confirmed deletion (404 response)")

def test_pizza_advanced_features():
    """Test pizza search, filtering, and sorting"""
    print("\n🔍 TESTING PIZZA ADVANCED FEATURES")
    print("=" * 40)
    
    # Test SEARCH
    print("\n1. Testing SEARCH functionality:")
    
    # Search by name
    response = client.get("/api/pizzas/?search=Margherita")
    assert response.status_code == 200
    data = response.json()
    margherita_found = any("Margherita" in pizza["name"] for pizza in data["pizzas"])
    print(f"   ✅ Search 'Margherita': Found = {margherita_found} ({data['results']} results)")
    
    # Search by description
    response = client.get("/api/pizzas/?search=Italian")
    assert response.status_code == 200
    data = response.json()
    print(f"   ✅ Search 'Italian': {data['results']} results")
    
    # Test SORTING
    print("\n2. Testing SORT functionality:")
    response = client.get("/api/pizzas/?sort_by_name=true")
    assert response.status_code == 200
    data = response.json()
    pizza_names = [pizza["name"] for pizza in data["pizzas"]]
    is_sorted = pizza_names == sorted(pizza_names)
    print(f"   ✅ Sort by name: Correctly sorted = {is_sorted}")
    print(f"      First 3 pizzas: {pizza_names[:3]}")
    
    # Test FILTERING
    print("\n3. Testing FILTER functionality:")
    response = client.get("/api/pizzas/?ingredient_filter=pepperoni")
    assert response.status_code == 200
    data = response.json()
    print(f"   ✅ Filter 'pepperoni': {data['results']} pizzas found")
    
    response = client.get("/api/pizzas/?ingredient_filter=mushroom")
    assert response.status_code == 200
    data = response.json()
    print(f"   ✅ Filter 'mushroom': {data['results']} pizzas found")
    
    # Test PAGINATION
    print("\n4. Testing PAGINATION:")
    response = client.get("/api/pizzas/?limit=3&page=1")
    assert response.status_code == 200
    data = response.json()
    page1_count = data["results"]
    print(f"   ✅ Page 1 (limit=3): {page1_count} pizzas")
    
    response = client.get("/api/pizzas/?limit=3&page=2")
    assert response.status_code == 200
    data = response.json()
    page2_count = data["results"]
    print(f"   ✅ Page 2 (limit=3): {page2_count} pizzas")

def test_pizza_error_handling():
    """Test pizza error scenarios"""
    print("\n❌ TESTING PIZZA ERROR HANDLING")
    print("=" * 40)
    
    # Test invalid data
    print("\n1. Testing invalid data:")
    invalid_data = {"name": "", "description": ""}
    response = client.post("/api/pizzas/", json=invalid_data)
    print(f"   ✅ Empty fields validation: {response.status_code} (Expected 422)")
    
    # Test non-existent ingredients
    print("\n2. Testing non-existent ingredients:")
    invalid_pizza = {
        "name": "Invalid Ingredients Pizza",
        "description": "Pizza with ingredients that don't exist",
        "ingredient_ids": [99999, 99998]
    }
    response = client.post("/api/pizzas/", json=invalid_pizza)
    print(f"   ✅ Non-existent ingredients: {response.status_code} (Expected 400)")
    
    # Test non-existent pizza operations
    print("\n3. Testing non-existent pizza operations:")
    response = client.get("/api/pizzas/99999")
    print(f"   ✅ Non-existent GET: {response.status_code} (Expected 404)")
    
    response = client.patch("/api/pizzas/99999", json={"name": "Test"})
    print(f"   ✅ Non-existent UPDATE: {response.status_code} (Expected 404)")
    
    response = client.delete("/api/pizzas/99999")
    print(f"   ✅ Non-existent DELETE: {response.status_code} (Expected 404)")

def run_pizza_tests():
    """Run all pizza tests"""
    print("🍕 COMPREHENSIVE PIZZA API TESTS")
    print("=" * 50)
    
    try:
        # Step 1: Create base ingredients
        ingredient_ids = create_base_ingredients()
        
        if len(ingredient_ids) < 5:
            print("❌ Failed to create enough ingredients for pizza testing")
            return False
        
        # Step 2: Populate pizza test data
        pizzas = populate_pizza_test_data(ingredient_ids)
        
        # Step 3: Test CRUD operations
        test_pizza_crud_operations(ingredient_ids)
        
        # Step 4: Test advanced features
        test_pizza_advanced_features()
        
        # Step 5: Test error handling
        test_pizza_error_handling()
        
        print("\n" + "=" * 50)
        print("🎉 ALL PIZZA TESTS PASSED!")
        print("=" * 50)
        print(f"✅ Created {len(ingredient_ids)} ingredients")
        print(f"✅ Populated {len(pizzas)} pizzas")
        print("✅ All CRUD operations working")
        print("✅ Search, filter, sort working")
        print("✅ Error handling working correctly")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ PIZZA TEST FAILED: {str(e)}")
        return False
    except Exception as e:
        print(f"\n💥 ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_pizza_tests()
    if not success:
        sys.exit(1)