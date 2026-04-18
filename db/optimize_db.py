import sqlite3
import os

def add_database_indexes():
    """Add performance indexes to the database"""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'molding.db')
    
    try:
        conn = sqlite3.connect(db_path, timeout=30.0)  # Longer timeout
        cursor = conn.cursor()
        
        # Create indexes for better performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_sensor_readings_timestamp ON sensor_readings(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_sensor_readings_machine_id ON sensor_readings(machine_id)",
            "CREATE INDEX IF NOT EXISTS idx_sensor_readings_composite ON sensor_readings(machine_id, timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_alerts_resolved_severity ON alerts(resolved, severity)",
            "CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_quality_inspection_reading_id ON quality_inspection(reading_id)"
        ]
        
        print("Adding database indexes for better performance...")
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
                print(f"Created index: {index_sql}")
            except Exception as e:
                print(f"Error creating index: {e}")
        
        conn.commit()
        print("Database optimization complete!")
        
    except sqlite3.OperationalError as e:
        print(f"Database is locked. Please close other connections and try again.")
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    add_database_indexes()