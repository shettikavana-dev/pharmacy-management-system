
import sqlite3

DB_NAME = "pharmacy.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            expiry_date TEXT,
            supplier TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            medicine_id INTEGER,
            medicine_name TEXT,
            quantity INTEGER,
            unit_price REAL,
            gst REAL,
            total REAL,
            sale_date TEXT
        )
    """)

    conn.commit()
    conn.close()


def get_medicines():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medicines")
    data = cursor.fetchall()
    conn.close()
    return data


def add_medicine(name, category, price, quantity, expiry, supplier):
    conn = get_connection()
    conn.execute("""
        INSERT INTO medicines
        (name, category, price, quantity, expiry_date, supplier)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, category, price, quantity, expiry, supplier))
    conn.commit()
    conn.close()
