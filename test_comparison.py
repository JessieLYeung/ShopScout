from comparison import (
    compare_products,
    filter_products,
    group_products_by_type,
    normalize_size,
    parse_size,
)


def test_size_parsing_and_normalization():
    assert parse_size("12 ct") == {"amount": 12.0, "unit": "ct"}
    assert normalize_size("1 gal") == {
        "measurement_type": "volume",
        "quantity": 128,
    }


def test_comparison_groups_keep_product_variants_separate():
    products = [
        {
            "name": "Publix Whole Milk",
            "brand": None,
            "retailerName": "Publix",
            "price": 4.41,
            "size": "1 gal",
        },
        {
            "name": "Friendly Farms Whole Milk",
            "brand": "Friendly Farms",
            "retailerName": "ALDI",
            "price": 2.97,
            "size": "1 gal",
        },
        {
            "name": "Friendly Farms Almond Milk",
            "brand": "Friendly Farms",
            "retailerName": "ALDI",
            "price": 2.50,
            "size": "1 gal",
        },
    ]

    compared = compare_products(products)

    assert [item["comparison_group"] for item in compared] == [
        "Almond Milk",
        "Whole Milk",
        "Whole Milk",
    ]
    assert compared[1]["comparison_key"] == compared[2]["comparison_key"]


def test_filter_uses_whole_words_and_comparison_rejects_bad_prices():
    products = [
        {"name": "Ham"},
        {"name": "Hamburger Buns"},
        {"name": "Milk", "price": float("nan"), "size": "1 gal"},
        {"name": "Milk", "price": -1, "size": "1 gal"},
    ]

    assert filter_products(products, "ham") == [{"name": "Ham"}]
    assert compare_products(products[2:]) == []


def test_comparison_preserves_store_and_price_freshness_details():
    result = compare_products([{
        "name": "Whole Milk",
        "retailerName": "Publix",
        "price": 4.25,
        "size": "1 gal",
        "store_name": "Publix",
        "store_address": "123 Main St",
        "store_distance_km": 0.6,
        "availability": "unknown",
        "product_url": "https://example.com/milk",
        "last_updated": "2026-11-25 12:00:00",
    }])

    assert result[0]["store_address"] == "123 Main St"
    assert result[0]["store_distance_km"] == 0.6
    assert result[0]["availability"] == "unknown"
    assert result[0]["product_url"] == "https://example.com/milk"
    assert result[0]["last_updated"] == "2026-11-25 12:00:00"


def test_group_products_by_measurement_type():
    grouped = group_products_by_type([
        {"measurement_type": "volume"},
        {"measurement_type": "count"},
    ])

    assert len(grouped["volume"]) == 1
    assert len(grouped["count"]) == 1
    assert grouped["weight"] == []
