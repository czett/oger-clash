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

                cur.execute(
                    """
                    INSERT INTO user_inventory (user_id, item_id, quantity)
                    SELECT %s, id, 0 FROM items
                    """,
                    (user_id,)
                )

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
                cur.execute(
                    """
                    SELECT id FROM categories
                    WHERE name = %s
                    """,
                    (category_name,)
                )
                existing_category = cur.fetchone()

                if not existing_category:
                    cur.execute(
                        """
                        INSERT INTO categories (name)
                        VALUES (%s)
                        """,
                        (category_name,)
                    )
        return True
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()

def insert_product_if_not_exists(name: str, price: int, category_name: str):
    insert_category_if_not_exists(category_name)
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id FROM items
                    WHERE name = %s AND price = %s
                    """,
                    (name, price)
                )
                existing_product = cur.fetchone()

                if not existing_product:
                    cur.execute(
                        """
                        INSERT INTO items (name, price, category_id)
                        SELECT %s, %s, c.id FROM categories c WHERE c.name = %s
                        """,
                        (name, price, category_name)
                    )
        return True
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()

def get_inventory(user_id: int):
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT i.name, ui.quantity, i.price
                    FROM user_inventory ui
                    JOIN items i ON ui.item_id = i.id
                    WHERE ui.user_id = %s
                    """,
                    (user_id,)
                )
                inventory = cur.fetchall()
                inventory_list = [{"name": item[0], "quantity": item[1], "price": item[2]} for item in inventory]

        return True, inventory_list
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()

# Other functions like `add_item_to_inventory`, `remove_item_from_inventory`, etc.
# can be similarly refactored by replacing psycopg2-specific code with psycopg.

