
import re

# Convert supported units into a common measurement.
# Volume -> fluid ounces
# Weight -> ounces
# Count -> individual items

UNIT_CONVERSIONS = {
    "gal": ("volume", 128),
    "fl oz": ("volume", 1),
    "l": ("volume", 33.814),
    "ml": ("volume", 0.033814),

    "lb": ("weight", 16),
    "oz": ("weight", 1),
    "kg": ("weight", 35.274),
    "g": ("weight", 0.035274),

    "ct": ("count", 1),
    "count": ("count", 1),
    "roll": ("count", 1),
    "rolls": ("count", 1),
}


def parse_size(size):
    # Extract the quantity and unit from a product size.
    size = size.lower().strip()

    match = re.fullmatch(
        r"(\d+(?:\.\d+)?)\s*(fl oz|rolls|roll|count|gal|ml|kg|lb|oz|ct|l|g)",
        size
    )

    if match is None:
        return None

    amount = float(match.group(1))
    unit = match.group(2)

    return {
        "amount": amount,
        "unit": unit
    }


def normalize_size(size):
    parsed = parse_size(size)

    if parsed is None:
        return None

    amount = parsed["amount"]
    unit = parsed["unit"]

    measurement_type, conversion_factor = UNIT_CONVERSIONS[unit]

    normalized_amount = amount * conversion_factor

    return {
        "measurement_type": measurement_type,
        "quantity": normalized_amount
    }


def calculate_unit_price(price, quantity):
    if quantity <= 0:
        return None

    return price / quantity


def compare_products(products):
    compared_products = []

    for product in products:
        size = product.get("size")
        price = product.get("price")

        if not size or price is None:
            continue

        normalized = normalize_size(size)

        if normalized is None:
            continue

        # Milk sizes listed in oz represent fluid ounces, not weight.
        if (
            normalized["measurement_type"] == "weight"
            and "milk" in product.get("name", "").lower()
            and size.lower().strip().endswith("oz")
        ):
            normalized["measurement_type"] = "volume"

        quantity = normalized["quantity"]

        if quantity <= 0:
            continue

        unit_price = calculate_unit_price(price, quantity)

        compared_products.append({
            "name": product.get("name"),
            "retailer": product.get("retailerName"),
            "price": price,
            "size": size,
            "measurement_type": normalized["measurement_type"],
            "unit_price": round(unit_price, 4)
        })

    return sorted(
        compared_products,
        key=lambda product: product["unit_price"]
    )

def filter_products(products, search_query):
    keywords = search_query.lower().split()
    filtered_products = []

    for product in products:
        name = product.get("name", "").lower()

        if all(keyword in name for keyword in keywords):
            filtered_products.append(product)

    return filtered_products

def group_products_by_type(products):
    groups = {
        "volume": [],
        "weight": [],
        "count": []
    }

    for product in products:
        measurement_type = product["measurement_type"]
        groups[measurement_type].append(product)

    return groups
