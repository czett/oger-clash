import bcrypt
import psycopg
from datetime import datetime
import json, random

with open("credentials.yml", "r") as creds:
    pw = creds.readlines()[0]

DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": pw,
    "host": "db.uldmvuvkaoflwdcfhsev.supabase.co",
    "port": 5432,
}

def get_db_connection():
    return psycopg.connect(**DB_CONFIG)

def register(username: str, password: str):
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users (username, password, created_at)
                    VALUES (%s, %s, %s) RETURNING id
                    """,
                    (username, hashed_password.decode(), datetime.now())
                )
                user_id = cur.fetchone()[0]

                cur.execute("""
                    INSERT INTO user_inventory (user_id, item_id, quantity)
                    SELECT %s, id, 0 FROM items
                """, (user_id,))

        return True, "Success"
    except psycopg.errors.UniqueViolation:
        return False, "Username already exists"
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()

def login(username: str, password: str):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT password FROM users WHERE username = %s", (username,))
            user = cur.fetchone()
            if user and bcrypt.checkpw(password.encode(), user[0].encode()):
                return True, "Success"
            else:
                return False, "Wrong username or password"
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()

def insert_category_if_not_exists(category_name: str):
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                # Überprüfen, ob die Kategorie existiert
                cur.execute("""
                    SELECT id FROM categories
                    WHERE name = %s
                """, (category_name,))
                existing_category = cur.fetchone()

                if not existing_category:
                    # Wenn die Kategorie nicht existiert, füge sie ein
                    cur.execute("""
                        INSERT INTO categories (name)
                        VALUES (%s)
                    """, (category_name,))
        return True
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()

def insert_product_if_not_exists(name: str, price: int, category_name: str):
    # Sicherstellen, dass die Kategorie existiert
    insert_category_if_not_exists(category_name)
    
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                # Überprüfen, ob das Produkt bereits existiert
                cur.execute("""
                    SELECT id FROM items
                    WHERE name = %s AND price = %s
                """, (name, price))
                existing_product = cur.fetchone()

                if not existing_product:
                    # Wenn das Produkt nicht existiert, füge es in die Datenbank ein
                    cur.execute("""
                        INSERT INTO items (name, price, category_id)
                        SELECT %s, %s, c.id FROM categories c WHERE c.name = %s
                    """, (name, price, category_name))

        return True
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()

def get_products():
    # Lade die JSON-Daten
    with open("static/gameplay/shop/offers/products.json", "r") as file:
        cats = json.load(file)["categories"]

    products = []

    for cat in cats:
        lc = len(cats[cat])
        if lc > 3:
            for i in range(lc - 3):
                cats[cat].pop(random.randint(-1 + len(cats[cat])))

        for product in cats[cat]:
            name = product["name"]
            price = product["price"]

            insert_product_if_not_exists(name, price, cat)

        products.append([cat, cats[cat]])

    return products

def add_item_to_inventory(user_id: int, item_id: int, quantity: int):
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                # Überprüfen, ob das Item bereits im Inventar des Benutzers existiert
                cur.execute("""
                    SELECT quantity FROM user_inventory
                    WHERE user_id = %s AND item_id = %s
                """, (user_id, item_id))
                existing_quantity = cur.fetchone()

                if existing_quantity:
                    # Wenn das Item schon im Inventar ist, Menge aktualisieren
                    new_quantity = existing_quantity[0] + quantity
                    cur.execute("""
                        UPDATE user_inventory
                        SET quantity = %s
                        WHERE user_id = %s AND item_id = %s
                    """, (new_quantity, user_id, item_id))
                else:
                    # Wenn das Item noch nicht im Inventar ist, neuen Eintrag hinzufügen
                    cur.execute("""
                        INSERT INTO user_inventory (user_id, item_id, quantity)
                        VALUES (%s, %s, %s)
                    """, (user_id, item_id, quantity))
        return True, "Item added successfully"
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()

def remove_item_from_inventory(user_id: int, item_id: int):
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                # Item aus dem Inventar des Benutzers entfernen
                cur.execute("""
                    DELETE FROM user_inventory
                    WHERE user_id = %s AND item_id = %s
                """, (user_id, item_id))
        return True, "Item removed successfully"
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()

def get_inventory(user_id: int):
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                # Abrufen des Inventars für den angegebenen Benutzer
                cur.execute("""
                    SELECT i.name, ui.quantity, i.price
                    FROM user_inventory ui
                    JOIN items i ON ui.item_id = i.id
                    WHERE ui.user_id = %s
                """, (user_id,))
                inventory = cur.fetchall()
                
                # Formatieren der Ergebnisse als Liste von Dictionarien
                inventory_list = [{"name": item[0], "quantity": item[1], "price": item[2]} for item in inventory]
                
        return True, inventory_list
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()

def clear_inventory(user_id: int):
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                # Löschen aller Items aus dem Inventar des Benutzers
                cur.execute("""
                    DELETE FROM user_inventory
                    WHERE user_id = %s
                """, (user_id,))
        return True, "Inventory cleared successfully"
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()

def get_item_id_by_name(name: str):
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                # Sucht nach der item_id anhand des Namens des Produkts
                cur.execute("""
                    SELECT id FROM items
                    WHERE name = %s
                """, (name,))
                item_id = cur.fetchone()

                if item_id:
                    return item_id[0]  # Rückgabe der ID des gefundenen Items
                else:
                    return None  # Falls das Item nicht gefunden wurde
    except Exception as e:
        return None, f"Error: {e}"
    finally:
        conn.close()

def get_user_id_by_nick(nick: str):
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                # Sucht nach der user_id anhand des Nicknames des Benutzers
                cur.execute("""
                    SELECT id FROM users
                    WHERE username = %s
                """, (nick,))
                user_id = cur.fetchone()

                if user_id:
                    return user_id[0]  # Rückgabe der ID des gefundenen Benutzers
                else:
                    return None  # Falls der Benutzer nicht gefunden wurde
    except Exception as e:
        return None, f"Error: {e}"
    finally:
        conn.close()

def add_diamonds_to_user(user_id, amount):
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                # Diamanten für den Benutzer erhöhen
                cur.execute("""
                    UPDATE users
                    SET diamonds = diamonds + %s
                    WHERE id = %s
                """, (amount, user_id))
        return True
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()

def subtract_diamonds_from_user(user_id: int, amount: int):
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET diamonds = diamonds - %s WHERE id = %s AND diamonds >= %s",
                    (amount, user_id, amount)
                )
                if cur.rowcount == 0:
                    raise ValueError("Not enough diamonds")
    except Exception as e:
        raise e
    finally:
        conn.close()

def get_diamonds_for_user(user_id):
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                # Abrufen der Diamanten des Benutzers
                cur.execute("""
                    SELECT diamonds FROM users
                    WHERE id = %s
                """, (user_id,))
                diamonds = cur.fetchone()

                if diamonds:
                    return diamonds[0]  # Rückgabe der Diamantenanzahl
                else:
                    return 0  # Wenn der Benutzer keine Diamanten hat
    except Exception as e:
        return 0, f"Error: {e}"
    finally:
        conn.close()