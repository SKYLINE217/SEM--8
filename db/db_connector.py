import sqlite3
import os

# DBMS Layer Requirement: SQLite interface with insert/query methods
class DBConnector:
    def __init__(self, db_path=None):
        if db_path is None:
            self.db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'molding.db')
        else:
            self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._init_db()

    def _init_db(self):
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=15)
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA journal_mode=WAL;")
        # Enable foreign keys
        self.cursor.execute("PRAGMA foreign_keys = ON;")
        
        # Load schema
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r') as f:
            self.cursor.executescript(f.read())
        
        # Ensure at least one machine exists
        self.cursor.execute("INSERT OR IGNORE INTO machines (machine_id) VALUES (1)")
        self.conn.commit()

    def insert_reading(self, machine_id, timestamp, temp_upper, temp_lower, pressure, state):
        self.cursor.execute('''
            INSERT INTO sensor_readings (machine_id, timestamp, platen_temp_upper, platen_temp_lower, hydraulic_pressure, cycle_state)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (machine_id, timestamp, temp_upper, temp_lower, pressure, state))
        self.conn.commit()
        return self.cursor.lastrowid

    def insert_inspection(self, reading_id, density, hardness, defects):
        self.cursor.execute('''
            INSERT INTO quality_inspection (reading_id, density, hardness_shore_a, visual_defects)
            VALUES (?, ?, ?, ?)
        ''', (reading_id, density, hardness, defects))
        self.conn.commit()

    def get_readings(self, limit=100):
        self.cursor.execute("SELECT * FROM sensor_readings ORDER BY timestamp DESC LIMIT ?", (limit,))
        return self.cursor.fetchall()
    
    def get_alerts(self):
        self.cursor.execute("SELECT * FROM alerts ORDER BY timestamp DESC")
        return self.cursor.fetchall()

    def close(self):
        if self.conn:
            self.conn.close()
