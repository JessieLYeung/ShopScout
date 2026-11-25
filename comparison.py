
import math
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


def _comparison_group(product):
    name = str(product.get("name") or "")
    descriptor = name

    terms_to_remove = [
        product.get("brand"),
        product.get("retailerName"),
        product.get("size"),
        "Publix",
        "Aldi",
        "Sprouts Farmers Market",
        "Sprouts",
    ]

    for term in terms_to_remove:
        if term:
            descriptor = re.sub(
                rf"\b{re.escape(str(term))}\b",
                " ",
                descriptor,
                flags=re.IGNORECASE,
            )

    descriptor = re.sub(r"[^a-zA-Z0-9]+", " ", descriptor).strip()
    descriptor = re.sub(r"\s+", " ", descriptor)
    if not descriptor:
        descriptor = name.strip()

    return descriptor.casefold(), descriptor


def compare_products(products):
    compared_products = []

    for product in products:
        size = product.get("size")
        price = product.get("price")

        if not size or price is None:
            continue

        try:
            price = float(price)
        except (TypeError, ValueError):
            continue

        if not math.isfinite(price) or price < 0:
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
        comparison_key, comparison_label = _comparison_group(product)

        compared_products.append({
            "name": product.get("name"),
            "brand": product.get("brand"),
            "retailer": product.get("retailerName"),
            "price": price,
            "size": size,
            "measurement_type": normalized["measurement_type"],
            "unit_price": round(unit_price, 4),
            "comparison_key": comparison_key,
            "comparison_group": comparison_label,
            "store_name": product.get("store_name"),
            "store_address": product.get("store_address"),
            "store_distance_km": product.get("store_distance_km"),
            "availability": product.get("availability", "unknown"),
            "product_url": product.get("product_url"),
            "last_updated": product.get("last_updated"),
        })

    return sorted(
        compared_products,
        key=lambda product: product["unit_price"]
    )

def filter_products(products, search_query):
    keywords = re.findall(r"[a-z0-9]+", search_query.casefold())
    filtered_products = []

    for product in products:
        name = str(product.get("name") or "").casefold()
        name_words = set(re.findall(r"[a-z0-9]+", name))

        if all(keyword in name_words for keyword in keywords):
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
