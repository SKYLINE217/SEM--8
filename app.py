import streamlit as st
import threading
import sys
import os

# Ensure the root directory is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cndc.mqtt_gateway import MQTTGateway
from cndc.network_simulator import NetworkSimulator
from db.db_connector import DBConnector
from simulation.sensor_simulator import SensorSimulator
from run_prototype import run_simulation

@st.cache_resource
def start_simulation():
    print("--> Initializing Background Simulation Thread...")
    network_sim = NetworkSimulator()
    mqtt_gateway = MQTTGateway(network_sim)
    mqtt_gateway.connect()
    
    db = DBConnector()
    sensor_sims = [SensorSimulator(machine_id=i) for i in range(1, 7)]
    
    sim_thread = threading.Thread(target=run_simulation, args=(sensor_sims, mqtt_gateway, db, network_sim), daemon=True)
    sim_thread.start()
    return True

# Start background simulation (st.cache_resource ensures it only runs once per app lifecycle)
start_simulation()

# Import and execute the dashboard natively
import dashboard.app as dashboard_ui
dashboard_ui.main()
