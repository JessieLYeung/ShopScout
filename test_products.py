from database import get_db_connection
from products import add_product, add_store_listing, search_product_listings

# Add a test store
connection = get_db_connection()
cursor = connection.cursor()

cursor.execute("""
    INSERT INTO Stores (store_name, address, latitude, longitude)
    VALUES (?, ?, ?, ?)
""", ("Walmart", "Orlando, FL", 28.5421, -81.3790))

store_id = cursor.lastrowid
connection.commit()
connection.close()

# Add a test product
product_id = add_product(
    "Coca-Cola Original",
    "Coca-Cola",
    "Beverages",
    "12 x 12 fl oz"
)
print("Product ID returned:", product_id)

# Connect the product to the store
add_store_listing(
    product_id,
    store_id,
    price=7.99,
    availability="available",
    product_url="https://www.walmart.com/"
)

# Search for the product and its listings
results = search_product_listings("Coca-Cola")

for result in results:
    print(dict(result))