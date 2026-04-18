import sqlite3
import os

def get_connection():
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'molding.db')
    return sqlite3.connect(db_path)

def seed():
    conn = get_connection()
    cursor = conn.cursor()
    
    print("Dropping existing machines table...")
    cursor.execute("DROP TABLE IF EXISTS machines")
    
    print("Recreating machines table with machine_name column...")
    cursor.execute("""
        CREATE TABLE machines (
            machine_id INTEGER PRIMARY KEY,
            machine_name TEXT
        )
    """)
    
    machines = [
        (1, 'Molding-Press-01 (Hydraulic)'),
        (2, 'Molding-Press-02 (Pneumatic)'),
        (3, 'Molding-Press-03 (Electric)'),
        (4, 'Molding-Press-04 (Hybrid)'),
        (5, 'Molding-Press-05 (Hydraulic-B)'),
        (6, 'Molding-Press-06 (Pneumatic-B)')
    ]
    
    print("Inserting machine data...")
    for m_id, m_name in machines:
        cursor.execute("INSERT INTO machines (machine_id, machine_name) VALUES (?, ?)", (m_id, m_name))
    
    conn.commit()
    conn.close()
    print("Seed complete: 6 machines initialized.")

if __name__ == "__main__":
    seed()
