import pytest

import database
from products import add_product, add_store_listing, search_product_listings


@pytest.fixture
def temporary_database(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "shopscout.db")
    database.create_tables()
    return database.DATABASE_PATH


def test_product_listing_can_be_added_and_updated(temporary_database):
    connection = database.get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO Stores (store_name, address, latitude, longitude)
        VALUES (?, ?, ?, ?)
        """,
        ("Publix", "123 Main St, Orlando, FL", 28.54, -81.38),
    )
    store_id = cursor.lastrowid
    connection.commit()
    connection.close()

    product_id = add_product(
        "Whole Milk",
        "Example Farms",
        "Dairy",
        "1 gal",
    )
    add_store_listing(
        product_id,
        store_id,
        price=4.25,
        availability="available",
        product_url="https://example.com/milk",
    )
    add_store_listing(
        product_id,
        store_id,
        price=4.50,
        availability="out_of_stock",
    )

    results = search_product_listings("Whole Milk")

    assert len(results) == 1
    assert results[0]["price"] == 4.50
    assert results[0]["availability"] == "out_of_stock"
    assert results[0]["product_url"] is None
