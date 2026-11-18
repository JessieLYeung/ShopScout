from products import find_products

products = find_products("milk", "32801", [])

print(f"Number of products found: {len(products)}")
for product in products:
    print(product["name"], product["price"], product["retailerName"])