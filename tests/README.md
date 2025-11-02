# Pizza API Test Suite

Comprehensive tests for the Pizza API project that populate data and test all CRUD endpoints.

## 📁 Test Files

### 🎯 **Main Test Files (Choose One)**

1. **`test_pizza_comprehensive.py`** ⭐ **RECOMMENDED**
   - Complete end-to-end test suite
   - Tests ingredients + pizzas + advanced features
   - **Run:** `python tests/test_pizza_comprehensive.py`

2. **`test_ingredients.py`** - Focused Ingredient Tests
   - Comprehensive ingredient data population (40+ ingredients)
   - All ingredient CRUD operations
   - **Run:** `python tests/test_ingredients.py`

3. **`test_pizzas.py`** - Focused Pizza Tests
   - Comprehensive pizza data population (10+ pizzas)
   - All pizza CRUD operations + advanced features
   - **Run:** `python tests/test_pizzas.py`

### 🚀 **Test Runner**

- **`run_tests.py`** - Convenient test runner
  - **Run all tests:** `python tests/run_tests.py`
  - **Show test info:** `python tests/run_tests.py --info`

## 🧪 What the Tests Do

### 1. 🧄 **Ingredient Data Population**
Creates comprehensive test data including:
- **Basic ingredients:** Tomato sauce, mozzarella, pepperoni, mushrooms, etc.
- **Meat toppings:** Ham, bacon, sausage, chicken, etc.
- **Vegetables:** Spinach, artichokes, peppers, onions, etc.
- **Cheese varieties:** Parmesan, feta, cheddar, goat cheese, etc.
- **Sauces:** BBQ, white sauce, pesto, etc.
- **Allergens:** Wheat, milk, eggs, soy, gluten, nuts, etc.
- **Complex ingredients:** Pizza dough, cheese blends, seasoning mixes

**Total:** 40+ ingredients including allergens and sub-ingredients

### 2. 🍕 **Pizza Data Population**
Creates diverse pizza test data:
- **Classic Margherita** - Traditional Italian with basil
- **Pepperoni Classic** - America's favorite
- **Supreme Special** - Loaded with everything
- **Meat Lovers** - Multiple meat toppings
- **Vegetarian Garden** - Fresh vegetables
- **Hawaiian Paradise** - Ham and pineapple
- **Italian Sausage Special** - Savory sausage combo
- **And more...**

**Total:** 10+ different pizza varieties

### 3. 🔧 **CRUD Endpoint Testing**

#### Ingredient CRUD:
- ✅ **CREATE** - Add new ingredients
- ✅ **READ ALL** - List all ingredients
- ✅ **READ ONE** - Get specific ingredient
- ✅ **UPDATE** - Modify ingredient properties
- ✅ **DELETE** - Remove ingredient

#### Pizza CRUD:
- ✅ **CREATE** - Add new pizzas with ingredients
- ✅ **READ ALL** - List all pizzas
- ✅ **READ ONE** - Get specific pizza with details
- ✅ **UPDATE** - Modify pizza name, description, ingredients
- ✅ **DELETE** - Remove pizza

### 4. 🔍 **Advanced Features Testing**

#### Search & Filter:
- ✅ **Search by name** - Find pizzas by name keywords
- ✅ **Search by description** - Find pizzas by description text
- ✅ **Filter by ingredients** - Find pizzas containing specific ingredients
- ✅ **Sort alphabetically** - Order pizzas by name
- ✅ **Pagination** - Test limit/page parameters

#### Business Logic:
- ✅ **Allergen detection** - Identify potential allergens
- ✅ **Ingredient relationships** - Test ingredient associations
- ✅ **Data validation** - Ensure proper data formats

### 5. ❌ **Error Handling Testing**
- ✅ **404 errors** - Non-existent resources
- ✅ **422 errors** - Invalid data validation
- ✅ **400 errors** - Business logic violations
- ✅ **Edge cases** - Empty data, invalid IDs, etc.

## 🚀 Quick Start

### Option 1: Run Everything (Recommended)
```bash
# Run comprehensive test suite
python tests/test_pizza_comprehensive.py
```

### Option 2: Run Specific Tests
```bash
# Test only ingredients
python tests/test_ingredients.py

# Test only pizzas  
python tests/test_pizzas.py
```

### Option 3: Use Test Runner
```bash
# Run with nice output
python tests/run_tests.py

# Show what tests do
python tests/run_tests.py --info
```

## 📊 Expected Output

When tests run successfully, you'll see:

```
🍕 COMPREHENSIVE PIZZA API TEST SUITE
============================================================

📊 PHASE 1: DATA POPULATION
----------------------------------------
🧄 Populating Ingredient Test Data...
  ✅  Tomato Sauce (ID: 1)
  ✅  Mozzarella Cheese (ID: 2)
  ✅  Pepperoni (ID: 3)
  ...
  ⚠️  Wheat Flour (ID: 35) - ALLERGEN
  ⚠️  Milk (ID: 36) - ALLERGEN
✅ Total ingredients created: 40

🍕 Populating Pizza Test Data...
  1. ✅ Classic Margherita (ID: 1) - 3 ingredients
  2. ✅ Pepperoni Classic (ID: 2) - 3 ingredients
  ...
✅ Total pizzas created: 10

🧄 PHASE 2: INGREDIENT CRUD TESTS
----------------------------------------
✅ Created ingredient: Test Parmesan Cheese
✅ Retrieved 41 ingredients
✅ Updated ingredient: Updated Test Ingredient
✅ Deleted ingredient with ID: 42

🍕 PHASE 3: PIZZA CRUD TESTS
----------------------------------------
✅ Created pizza: Test Custom Pizza
✅ Retrieved 11 pizzas
✅ Updated pizza: Updated Test Pizza
✅ Deleted pizza with ID: 11

🔍 PHASE 4: ADVANCED FEATURE TESTS
----------------------------------------
✅ Search by name 'Margherita': Found = True
✅ Pizzas sorted alphabetically: True
✅ Filter by 'pepperoni': Found 3 pizzas

❌ PHASE 5: ERROR HANDLING TESTS
----------------------------------------
✅ Non-existent ingredient: 404 (Expected 404)
✅ Invalid pizza data: 422 (Expected 422)

============================================================
🎉 ALL TESTS COMPLETED SUCCESSFULLY!
============================================================
```

## 🔧 Requirements

- **No external dependencies** - Uses FastAPI's built-in TestClient
- **SQLite database** - Creates temporary test database
- **Python 3.7+** - Standard library only

## 🛠️ Troubleshooting

### Common Issues:

1. **Import errors**
   ```bash
   # Make sure you're in the project root
   cd /path/to/ingest_test
   python tests/test_pizza_comprehensive.py
   ```

2. **Database errors**
   - Tests create their own SQLite database
   - No setup required

3. **API endpoint errors**
   - Check that your models and endpoints are properly defined
   - Tests will show specific error messages

### Debug Mode:
Tests include detailed output showing:
- ✅ Successful operations
- ❌ Failed operations with error details
- 📊 Summary statistics

## 📈 Test Coverage

The tests verify all major API functionality:

### Endpoints Tested:
- `POST /api/ingredients/` - Create ingredient
- `GET /api/ingredients/` - List ingredients
- `GET /api/ingredients/{id}` - Get ingredient
- `PATCH /api/ingredients/{id}` - Update ingredient
- `DELETE /api/ingredients/{id}` - Delete ingredient
- `POST /api/pizzas/` - Create pizza
- `GET /api/pizzas/` - List pizzas (with search/filter/sort)
- `GET /api/pizzas/{id}` - Get pizza
- `PATCH /api/pizzas/{id}` - Update pizza
- `DELETE /api/pizzas/{id}` - Delete pizza

### Data Coverage:
- **40+ ingredients** including allergens
- **10+ pizzas** with diverse ingredient combinations
- **Error scenarios** for all endpoints
- **Advanced features** like search, filter, sort, pagination

Your Pizza API will be thoroughly tested! 🍕✅