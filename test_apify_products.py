from products import find_products
from products import search_product_listings

products = find_products(
    "milk",
    "32801",
    [{
        "name": "Publix",
        "address": "400 E Central Blvd, Orlando, FL 32801",
        "latitude": 28.545179,
        "longitude": -81.373291
    }]
)

print("Number of products found:", len(products))

if products:
    print("First product:")
    print(products[0])

print("\nProducts saved in database:")

results = search_product_listings("milk")

for result in results:
    print(dict(result))