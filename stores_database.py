from database import get_db_connection


def save_store(store_name, address, latitude, longitude):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT store_id
        FROM Stores
        WHERE store_name = ?
          AND address = ?
    """, (store_name, address))

    existing_store = cursor.fetchone()

    if existing_store:
        connection.close()
        return existing_store["store_id"]

    cursor.execute("""
        INSERT INTO Stores (
            store_name,
            address,
            latitude,
            longitude
        )
        VALUES (?, ?, ?, ?)
    """, (store_name, address, latitude, longitude))

    store_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return store_id

def save_nearby_stores(stores):
    store_ids = []

    for store in stores:
        store_id = save_store(
            store["name"],
            store["address"],
            store["latitude"],
            store["longitude"]
        )

        store_ids.append(store_id)

    return store_ids

def get_all_stores():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM Stores")

    stores = cursor.fetchall()
    connection.close()

    return stores