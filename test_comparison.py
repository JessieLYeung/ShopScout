from comparison import parse_size, normalize_size, compare_products, group_products_by_type, filter_products

# Test parsing
print(parse_size("128 fl oz"))
print(parse_size("0.5 gal"))
print(parse_size("12 ct"))

# Test normalization
print(normalize_size("1 gal"))
print(normalize_size("2 lb"))
print(normalize_size("12 ct"))

# Test product comparisons
products = [
    {
        "name": "Publix Whole Milk",
        "retailerName": "Publix",
        "price": 4.41,
        "size": "1 gal"
    },
    {
        "name": "Friendly Farms Whole Milk",
        "retailerName": "ALDI",
        "price": 2.97,
        "size": "1 gal"
    },
    {
        "name": "Friendly Farms Whole Milk",
        "retailerName": "ALDI",
        "price": 1.95,
        "size": "0.5 gal"
    }
]

results = compare_products(products)

for product in results:
    print(product)

    products = [
    {"name": "Publix Whole Milk"},
    {"name": "Friendly Farms Whole Milk"},
    {"name": "Sprouts Organic Whole Milk"},
    {"name": "Publix 2% Reduced Fat Milk"},
    {"name": "Almond Milk"}
]

filtered = filter_products(products, "whole milk")

for product in filtered:
    print(product["name"])

assert len(filtered) == 3

print("Product filtering test passed!")

products = [
    {
        "name": "Publix Whole Milk",
        "retailerName": "Publix",
        "price": 4.41,
        "size": "1 gal"
    },
    {
        "name": "Friendly Farms Whole Milk",
        "retailerName": "ALDI",
        "price": 2.97,
        "size": "1 gal"
    },
    {
        "name": "Publix 2% Reduced Fat Milk",
        "retailerName": "Publix",
        "price": 4.41,
        "size": "1 gal"
    },
    {
        "name": "Sprouts Whole Milk",
        "retailerName": "Sprouts",
        "price": 2.99,
        "size": "0.5 gal"
    }
]

filtered = filter_products(products, "whole milk")
compared = compare_products(filtered)

for product in compared:
    print(product["name"], product["retailer"], product["unit_price"])

assert len(compared) == 3
assert compared[0]["retailer"] == "ALDI"

print("Filtering and comparison test passed!")

products = [
    {
        "name": "Whole Milk",
        "measurement_type": "volume",
        "unit_price": 0.03
    },
    {
        "name": "Chicken Breast",
        "measurement_type": "weight",
        "unit_price": 0.25
    },
    {
        "name": "Eggs",
        "measurement_type": "count",
        "unit_price": 0.30
    },
    {
        "name": "Orange Juice",
        "measurement_type": "volume",
        "unit_price": 0.05
    }
]

groups = group_products_by_type(products)

for measurement_type, items in groups.items():
    print(measurement_type, ":", len(items), "products")

assert len(groups["volume"]) == 2
assert len(groups["weight"]) == 1
assert len(groups["count"]) == 1

print("Product grouping test passed!")