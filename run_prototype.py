import time
import subprocess
import threading
import pandas as pd
import os
import sys

# Import modules
from cndc.mqtt_gateway import MQTTGateway
from cndc.network_simulator import NetworkSimulator
from db.db_connector import DBConnector
from simulation.sensor_simulator import SensorSimulator
from mat101.heat_transfer import HeatTransferSolver
from mat101.pressure_dynamics import PressureDynamicsSolver
from cs102.hash_table import HashTable

def run_simulation(sensor_sims, mqtt_gateway, db, network_sim):
    print("--> Starting Production Simulation (Continuous) for 6 Machines...")
    outage_triggered = False
    generators = [sim.generate_cycle_data(total_cycles=1000000) for sim in sensor_sims]
    
    while True:
        try:
            batch_data = [next(gen) for gen in generators]
            for i, (reading, inspection) in enumerate(batch_data):
                sim = sensor_sims[i]
                if i == 0 and reading['cycle_state'] == 'HEATING' and sim.cycle_count == 4 and not outage_triggered:
                    network_sim.simulate_outage(duration=3)
                    outage_triggered = True
                
                mqtt_gateway.publish_reading(reading)
                reading_id = db.insert_reading(
                    reading['machine_id'], 
                    reading['timestamp'], 
                    reading['platen_temp_upper'], 
                    reading['platen_temp_lower'], 
                    reading['hydraulic_pressure'], 
                    reading['cycle_state']
                )
                
                if inspection:
                    db.insert_inspection(
                        reading_id,
                        inspection['density'],
                        inspection['hardness_shore_a'],
                        inspection['visual_defects']
                    )
            
            time.sleep(1) # Slow down simulation to match real-time
        except StopIteration:
            break
        except Exception as e:
            print(f"Simulation error: {e}")
            time.sleep(1)

def main():
    print("=== Starting IoT-Enabled Compression Molding Prototype ===")
    
    recipes = HashTable()
    recipes.set('brake_shoe_A', {'temp': 165, 'pressure': 150, 'time': 180})
    
    network_sim = NetworkSimulator()
    mqtt_gateway = MQTTGateway(network_sim)
    mqtt_gateway.connect()
    
    db = DBConnector()
    sensor_sims = [SensorSimulator(machine_id=i) for i in range(1, 7)]
    
    # Start simulation in background thread
    sim_thread = threading.Thread(target=run_simulation, args=(sensor_sims, mqtt_gateway, db, network_sim), daemon=True)
    sim_thread.start()
    
    print("--> Launching Dashboard...")
    try:
        # Use sys.executable to ensure we use the same Python environment
        # Run from the script's directory so paths are consistent
        script_dir = os.path.dirname(os.path.abspath(__file__))
        subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard/app.py"], cwd=script_dir)
    except KeyboardInterrupt:
        print("\nStopping prototype...")
    except Exception as e:
        print(f"Failed to launch streamlit: {e}")


if __name__ == "__main__":
    main()
