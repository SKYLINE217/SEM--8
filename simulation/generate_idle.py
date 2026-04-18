import sqlite3
import time
import random
import os

def get_connection():
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'molding.db')
    return sqlite3.connect(db_path)

def run_idle_mode():
    conn = get_connection()
    cursor = conn.cursor()
    print("--> Resolving all critical alerts to normalize system status...")
    cursor.execute("UPDATE alerts SET resolved = 1 WHERE severity = 'CRITICAL'")
    conn.commit()
    print("--> Starting IDLE data generation (Safe Parameters)...")
    print("--> This will generate real-time data points to animate the dashboard.")
    print("--> Press Ctrl+C to stop.")
    last_temp = 30.0
    last_pressure = 0.02
    stuck_until = 0
    try:
        while True:
            import math
            t_val = time.time()
            temp_fluctuation = math.sin(t_val * 0.3) * 0.5
            temp = 30.0 + temp_fluctuation + random.uniform(-0.05, 0.05)
            pressure = 0.0 + random.uniform(0.01, 0.08)
            if time.time() < stuck_until:
                temp = last_temp
                pressure = last_pressure
            else:
                if random.random() < 0.01:
                    temp = temp + random.choice([-8, 10, 12])
                if random.random() < 0.01:
                    pressure = random.uniform(0.3, 0.6)
                if random.random() < 0.005:
                    stuck_until = time.time() + random.uniform(2, 4)
            state = "IDLE"
            timestamp = time.time()
            cursor.execute('''
                INSERT INTO sensor_readings (machine_id, timestamp, platen_temp_upper, platen_temp_lower, hydraulic_pressure, cycle_state)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (1, timestamp, temp, temp-1, pressure, state))
            conn.commit()
            print(f"Generated IDLE data: Temp={temp:.2f}, Press={pressure:.2f} at {time.strftime('%H:%M:%S')}")
            last_temp = temp
            last_pressure = pressure
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopped.")
    finally:
        conn.close()

if __name__ == "__main__":
    run_idle_mode()
