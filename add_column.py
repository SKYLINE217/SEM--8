import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'molding.db')
conn = sqlite3.connect(db_path)
try:
    conn.execute("ALTER TABLE machines ADD COLUMN control_mode TEXT DEFAULT 'AUTO'")
    conn.commit()
    print("Column control_mode added successfully.")
except sqlite3.OperationalError:
    print("Column control_mode already exists.")
conn.close()
