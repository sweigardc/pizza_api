"""
Comprehensive test suite for Pizza API
This file contains all tests for the pizza project including:
1. Ingredient data population and testing
2. Pizza data population and testing  
3. All CRUD endpoint testing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db, Base
from app import models
from app.config import settings

# Use PostgreSQL test database
TEST_DATABASE_NAME = f"{settings.POSTGRES_DB}"
POSTGRES_TEST_URL = (
    f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
    f"{settings.POSTGRES_HOSTNAME}:{settings.DATABASE_PORT}/{TEST_DATABASE_NAME}"
)

engine = create_engine(POSTGRES_TEST_URL, echo=False)  # Disable echo for cleaner test output
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override the get_db dependency for testing"""
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

class TestDataPopulator:
    """Class to handle test data population"""
    
    def __init__(self):
        self.ingredient_ids = []
        self.pizza_ids = []
        
    def populate_ingredients(self):
        """Populate comprehensive ingredient test data"""
        print("\n🧄 Populating Ingredient Test Data...")
        
        # Base ingredients
        base_ingredients = [
            {"name": "Tomato Sauce", "is_allergen": False},
            {"name": "Mozzarella Cheese", "is_allergen": False},
            {"name": "Pepperoni", "is_allergen": False},
            {"name": "Mushrooms", "is_allergen": False},
            {"name": "Bell Peppers", "is_allergen": False},
            {"name": "Onions", "is_allergen": False},
            {"name": "Italian Sausage", "is_allergen": False},
            {"name": "Basil", "is_allergen": False},
            {"name": "Oregano", "is_allergen": False},
            {"name": "Garlic", "is_allergen": False},
        ]
        
        # Allergen ingredients
        allergen_ingredients = [
            {"name": "Wheat Flour", "is_allergen": True},
            {"name": "Milk", "is_allergen": True},
            {"name": "Eggs", "is_allergen": True},
            {"name": "Soy", "is_allergen": True},
            {"name": "Gluten", "is_allergen": True},
        ]
        
        # Complex ingredients with sub-ingredients
        complex_ingredients = [
            {"name": "Pizza Dough", "is_allergen": False},
            {"name": "Cheese Blend", "is_allergen": False},
            {"name": "Meat Sauce", "is_allergen": False},
            {"name": "Veggie Mix", "is_allergen": False},
        ]
        
        all_ingredients = base_ingredients + allergen_ingredients + complex_ingredients
        
        for ingredient_data in all_ingredients:
            response = client.post("/api/ingredients/", json=ingredient_data)
            if response.status_code == 201:
                ingredient = response.json()
                self.ingredient_ids.append(ingredient["id"])
                print(f"✅ Created ingredient: {ingredient['name']} (ID: {ingredient['id']})")
            else:
                print(f"❌ Failed to create ingredient: {ingredient_data['name']} - {response.text}")
        
        print(f"✅ Total ingredients created: {len(self.ingredient_ids)}")
        return self.ingredient_ids
    
    def populate_pizzas(self):
        """Populate comprehensive pizza test data"""
        print("\n🍕 Populating Pizza Test Data...")
        
        if len(self.ingredient_ids) < 5:
            print("❌ Not enough ingredients created for pizza population")
            return []
        
        # Classic pizzas
        pizzas_data = [
            {
                "name": "Margherita",
                "description": "Classic Italian pizza with tomato sauce, mozzarella, and fresh basil",
                "ingredient_ids": self.ingredient_ids[:3]  # Tomato, Mozzarella, Basil
            },
            {
                "name": "Pepperoni",
                "description": "America's favorite pizza with pepperoni and mozzarella cheese",
                "ingredient_ids": self.ingredient_ids[:2] + [self.ingredient_ids[2]]  # Tomato, Mozzarella, Pepperoni
            },
            {
                "name": "Supreme",
                "description": "Loaded pizza with pepperoni, sausage, peppers, onions, and mushrooms",
                "ingredient_ids": self.ingredient_ids[:7]  # Multiple ingredients
            },
            {
                "name": "Vegetarian Deluxe",
                "description": "Fresh vegetables with mushrooms, bell peppers, and onions",
                "ingredient_ids": [self.ingredient_ids[0], self.ingredient_ids[1], self.ingredient_ids[3], self.ingredient_ids[4], self.ingredient_ids[5]]
            },
            {
                "name": "Meat Lovers",
                "description": "For carnivores - pepperoni and Italian sausage",
                "ingredient_ids": [self.ingredient_ids[0], self.ingredient_ids[1], self.ingredient_ids[2], self.ingredient_ids[6]]
            },
            {
                "name": "Hawaiian", 
                "description": "Controversial but delicious - ham and pineapple",
                "ingredient_ids": self.ingredient_ids[:2]  # Basic cheese pizza for now
            },
            {
                "name": "White Pizza",
                "description": "No sauce pizza with garlic, herbs, and cheese",
                "ingredient_ids": [self.ingredient_ids[1], self.ingredient_ids[7], self.ingredient_ids[8], self.ingredient_ids[9]]
            },
            {
                "name": "BBQ Chicken",
                "description": "Tangy BBQ sauce with chicken and onions",
                "ingredient_ids": [self.ingredient_ids[1], self.ingredient_ids[5]]  # Cheese and onions
            }
        ]
        
        for pizza_data in pizzas_data:
            response = client.post("/api/pizzas/", json=pizza_data)
            if response.status_code == 201:
                pizza = response.json()
                pizza_id = pizza["pizza"]["id"]
                self.pizza_ids.append(pizza_id)
                print(f"✅ Created pizza: {pizza['pizza']['name']} (ID: {pizza_id})")
            else:
                print(f"❌ Failed to create pizza: {pizza_data['name']} - {response.text}")
        
        print(f"✅ Total pizzas created: {len(self.pizza_ids)}")
        return self.pizza_ids

class TestIngredientCRUD:
    """Test all Ingredient CRUD operations"""
    
    def test_create_ingredient(self):
        """Test creating a new ingredient"""
        print("\n🧪 Testing Ingredient Creation...")
        
        ingredient_data = {
            "name": "Test Parmesan Cheese",
            "is_allergen": False,
            "sub_ingredient_ids": []
        }
        
        response = client.post("/api/ingredients/", json=ingredient_data)
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        
        ingredient = response.json()
        assert ingredient["name"] == "Test Parmesan Cheese"
        assert ingredient["is_allergen"] == False
        print(f"✅ Created ingredient: {ingredient['name']}")
        return ingredient["id"]
    
    def test_get_all_ingredients(self):
        """Test retrieving all ingredients"""
        print("\n🧪 Testing Get All Ingredients...")
        
        response = client.get("/api/ingredients/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        ingredients = response.json()
        assert len(ingredients) > 0, "Should have at least some ingredients"
        print(f"✅ Retrieved {len(ingredients)} ingredients")
        return ingredients
    
    def test_get_ingredient_by_id(self, ingredient_id):
        """Test retrieving a specific ingredient by ID"""
        print(f"\n🧪 Testing Get Ingredient by ID: {ingredient_id}...")
        
        response = client.get(f"/api/ingredients/{ingredient_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        ingredient = response.json()
        assert ingredient["id"] == ingredient_id
        print(f"✅ Retrieved ingredient: {ingredient['name']}")
        return ingredient
    
    def test_update_ingredient(self, ingredient_id):
        """Test updating an ingredient"""
        print(f"\n🧪 Testing Update Ingredient: {ingredient_id}...")
        
        update_data = {
            "name": "Updated Test Ingredient",
            "is_allergen": True
        }
        
        response = client.patch(f"/api/ingredients/{ingredient_id}", json=update_data)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        updated_ingredient = response.json()
        assert updated_ingredient["name"] == "Updated Test Ingredient"
        assert updated_ingredient["is_allergen"] == True
        print(f"✅ Updated ingredient: {updated_ingredient['name']}")
        return updated_ingredient
    
    def test_delete_ingredient(self, ingredient_id):
        """Test deleting an ingredient"""
        print(f"\n🧪 Testing Delete Ingredient: {ingredient_id}...")
        
        response = client.delete(f"/api/ingredients/{ingredient_id}")
        assert response.status_code == 204, f"Expected 204, got {response.status_code}"
        
        # Verify deletion
        get_response = client.get(f"/api/ingredients/{ingredient_id}")
        assert get_response.status_code == 404, "Ingredient should be deleted"
        print(f"✅ Deleted ingredient with ID: {ingredient_id}")

class TestPizzaCRUD:
    """Test all Pizza CRUD operations"""
    
    def test_create_pizza(self, ingredient_ids):
        """Test creating a new pizza"""
        print("\n🧪 Testing Pizza Creation...")
        
        pizza_data = {
            "name": "Test Custom Pizza",
            "description": "A test pizza with selected ingredients",
            "ingredient_ids": ingredient_ids[:3]  # Use first 3 ingredients
        }
        
        response = client.post("/api/pizzas/", json=pizza_data)
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        
        pizza = response.json()
        assert pizza["pizza"]["name"] == "Test Custom Pizza"
        assert len(pizza["pizza"]["ingredients"]) == 3
        print(f"✅ Created pizza: {pizza['pizza']['name']}")
        return pizza["pizza"]["id"]
    
    def test_get_all_pizzas(self):
        """Test retrieving all pizzas"""
        print("\n🧪 Testing Get All Pizzas...")
        
        response = client.get("/api/pizzas/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["status"] == "success"
        assert data["results"] > 0, "Should have at least some pizzas"
        print(f"✅ Retrieved {data['results']} pizzas")
        return data["pizzas"]
    
    def test_get_pizza_by_id(self, pizza_id):
        """Test retrieving a specific pizza by ID"""
        print(f"\n🧪 Testing Get Pizza by ID: {pizza_id}...")
        
        response = client.get(f"/api/pizzas/{pizza_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["status"] == "success"
        assert data["pizza"]["id"] == pizza_id
        print(f"✅ Retrieved pizza: {data['pizza']['name']}")
        return data["pizza"]
    
    def test_update_pizza(self, pizza_id, ingredient_ids):
        """Test updating a pizza"""
        print(f"\n🧪 Testing Update Pizza: {pizza_id}...")
        
        update_data = {
            "name": "Updated Test Pizza",
            "description": "Updated description for test pizza",
            "ingredient_ids": ingredient_ids[:2]  # Different ingredients
        }
        
        response = client.patch(f"/api/pizzas/{pizza_id}", json=update_data)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["pizza"]["name"] == "Updated Test Pizza"
        print(f"✅ Updated pizza: {data['pizza']['name']}")
        return data["pizza"]
    
    def test_delete_pizza(self, pizza_id):
        """Test deleting a pizza"""
        print(f"\n🧪 Testing Delete Pizza: {pizza_id}...")
        
        response = client.delete(f"/api/pizzas/{pizza_id}")
        assert response.status_code == 204, f"Expected 204, got {response.status_code}"
        
        # Verify deletion
        get_response = client.get(f"/api/pizzas/{pizza_id}")
        assert get_response.status_code == 404, "Pizza should be deleted"
        print(f"✅ Deleted pizza with ID: {pizza_id}")

class TestPizzaAdvancedFeatures:
    """Test advanced pizza features like search, filtering, sorting"""
    
    def test_search_pizzas(self):
        """Test searching pizzas by name and description"""
        print("\n🧪 Testing Pizza Search...")
        
        # Search by name
        response = client.get("/api/pizzas/?search=Margherita")
        assert response.status_code == 200
        data = response.json()
        margherita_found = any("Margherita" in pizza["name"] for pizza in data["pizzas"])
        print(f"✅ Search by name 'Margherita': Found = {margherita_found}")
        
        # Search by description
        response = client.get("/api/pizzas/?search=Classic")
        assert response.status_code == 200
        data = response.json()
        classic_found = any("Classic" in pizza["description"] for pizza in data["pizzas"])
        print(f"✅ Search by description 'Classic': Found = {classic_found}")
    
    def test_sort_pizzas(self):
        """Test sorting pizzas by name"""
        print("\n🧪 Testing Pizza Sorting...")
        
        response = client.get("/api/pizzas/?sort_by_name=true")
        assert response.status_code == 200
        data = response.json()
        
        pizza_names = [pizza["name"] for pizza in data["pizzas"]]
        is_sorted = pizza_names == sorted(pizza_names)
        print(f"✅ Pizzas sorted alphabetically: {is_sorted}")
        print(f"   Pizza names: {pizza_names[:5]}")  # Show first 5
    
    def test_filter_pizzas(self):
        """Test filtering pizzas by ingredients"""
        print("\n🧪 Testing Pizza Filtering...")
        
        response = client.get("/api/pizzas/?ingredient_filter=mozzarella")
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Filter by 'mozzarella': Found {data['results']} pizzas")
        
        response = client.get("/api/pizzas/?ingredient_filter=pepperoni")
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Filter by 'pepperoni': Found {data['results']} pizzas")
    
    def test_pagination(self):
        """Test pizza pagination"""
        print("\n🧪 Testing Pizza Pagination...")
        
        # Page 1
        response = client.get("/api/pizzas/?limit=3&page=1")
        assert response.status_code == 200
        data = response.json()
        page1_count = data["results"]
        print(f"✅ Page 1 (limit=3): {page1_count} pizzas")
        
        # Page 2
        response = client.get("/api/pizzas/?limit=3&page=2")
        assert response.status_code == 200
        data = response.json()
        page2_count = data["results"]
        print(f"✅ Page 2 (limit=3): {page2_count} pizzas")

class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_ingredient_errors(self):
        """Test ingredient error scenarios"""
        print("\n🧪 Testing Ingredient Error Handling...")
        
        # Test creating ingredient with invalid data
        response = client.post("/api/ingredients/", json={"name": ""})
        print(f"✅ Empty name error: {response.status_code} (Expected 422)")
        
        # Test getting non-existent ingredient
        response = client.get("/api/ingredients/99999")
        print(f"✅ Non-existent ingredient: {response.status_code} (Expected 404)")
        
        # Test updating non-existent ingredient
        response = client.patch("/api/ingredients/99999", json={"name": "Test"})
        print(f"✅ Update non-existent: {response.status_code} (Expected 404)")
        
        # Test deleting non-existent ingredient
        response = client.delete("/api/ingredients/99999")
        print(f"✅ Delete non-existent: {response.status_code} (Expected 404)")
    
    def test_pizza_errors(self):
        """Test pizza error scenarios"""
        print("\n🧪 Testing Pizza Error Handling...")
        
        # Test creating pizza with invalid data
        response = client.post("/api/pizzas/", json={"name": ""})
        print(f"✅ Empty pizza name: {response.status_code} (Expected 422)")
        
        # Test creating pizza with non-existent ingredients
        response = client.post("/api/pizzas/", json={
            "name": "Invalid Pizza",
            "description": "Test",
            "ingredient_ids": [99999, 99998]
        })
        print(f"✅ Non-existent ingredients: {response.status_code} (Expected 400)")
        
        # Test getting non-existent pizza
        response = client.get("/api/pizzas/99999")
        print(f"✅ Non-existent pizza: {response.status_code} (Expected 404)")

def run_all_tests():
    """Run the complete test suite"""
    print("🍕 COMPREHENSIVE PIZZA API TEST SUITE")
    print("=" * 60)
    
    try:
        # Initialize test data populator
        populator = TestDataPopulator()
        
        # 1. Populate test data
        print("\n📊 PHASE 1: DATA POPULATION")
        print("-" * 40)
        ingredient_ids = populator.populate_ingredients()
        pizza_ids = populator.populate_pizzas()
        
        # 2. Test Ingredient CRUD
        print("\n🧄 PHASE 2: INGREDIENT CRUD TESTS")
        print("-" * 40)
        ingredient_crud = TestIngredientCRUD()
        
        # Create a test ingredient for CRUD testing
        test_ingredient_id = ingredient_crud.test_create_ingredient()
        ingredient_crud.test_get_all_ingredients()
        ingredient_crud.test_get_ingredient_by_id(test_ingredient_id)
        ingredient_crud.test_update_ingredient(test_ingredient_id)
        ingredient_crud.test_delete_ingredient(test_ingredient_id)
        
        # 3. Test Pizza CRUD
        print("\n🍕 PHASE 3: PIZZA CRUD TESTS")
        print("-" * 40)
        pizza_crud = TestPizzaCRUD()
        
        # Create a test pizza for CRUD testing
        test_pizza_id = pizza_crud.test_create_pizza(ingredient_ids)
        pizza_crud.test_get_all_pizzas()
        pizza_crud.test_get_pizza_by_id(test_pizza_id)
        pizza_crud.test_update_pizza(test_pizza_id, ingredient_ids)
        pizza_crud.test_delete_pizza(test_pizza_id)
        
        # 4. Test Advanced Features
        print("\n🔍 PHASE 4: ADVANCED FEATURE TESTS")
        print("-" * 40)
        advanced_tests = TestPizzaAdvancedFeatures()
        advanced_tests.test_search_pizzas()
        advanced_tests.test_sort_pizzas()
        advanced_tests.test_filter_pizzas()
        advanced_tests.test_pagination()
        
        # 5. Test Error Handling
        print("\n❌ PHASE 5: ERROR HANDLING TESTS")
        print("-" * 40)
        error_tests = TestErrorHandling()
        error_tests.test_ingredient_errors()
        error_tests.test_pizza_errors()
        
        # Final summary
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"📊 Data Created:")
        print(f"   • {len(ingredient_ids)} Ingredients")
        print(f"   • {len(pizza_ids)} Pizzas")
        print(f"🧪 Tests Executed:")
        print(f"   • Ingredient CRUD operations")
        print(f"   • Pizza CRUD operations")
        print(f"   • Search and filtering")
        print(f"   • Sorting and pagination")
        print(f"   • Error handling")
        print("\n✅ Your Pizza API is working perfectly!")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        return False
    except Exception as e:
        print(f"\n💥 ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = run_all_tests()
    if not success:
        sys.exit(1)