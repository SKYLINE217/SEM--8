# Python Files Overview (Plain English)

This document explains what each Python file in this prototype does, in simple terms. It follows the data flow from simulation to storage and visualization.

## Top-Level Orchestrator

- [run_prototype.py](file:///d:/Riot%20Games/sem-8/molding_prototype/run_prototype.py)
  - Starts the end-to-end production simulation using all modules.
  - Creates components: network simulator, MQTT gateway, SQLite connector, sensor simulator, and math model validators.
  - Generates multiple cycles of sensor data, simulates a brief network outage, sends readings through MQTT, and stores them in SQLite.
  - Runs model validation to compare simulated data to physics models and saves validation plots.
  - Exports a CSV for later statistical analysis and attempts to run an R script.
  - Launches the Streamlit dashboard.

## Dashboard (Visualization)

- [app.py](file:///d:/Riot%20Games/sem-8/molding_prototype/dashboard/app.py)
  - A Streamlit app that reads recent data from the SQLite database and shows:
    - Current status, temperature, pressure, and last update time.
    - A simple “hydraulic press” visual that changes height during active phases.
    - Two live line charts (temperature and pressure) with red markers for anomalies.
    - Alerts table and a daily quality summary view if available.
  - Automatically refreshes every ~2 seconds to present live data.

## Simulation (Data Generation)

- [sensor_simulator.py](file:///d:/Riot%20Games/sem-8/molding_prototype/simulation/sensor_simulator.py)
  - Creates realistic production-cycle data guided by a state machine (IDLE → HEATING → COMPRESSION → CURING → EJECTION).
  - Temperature: smooth rise toward the target during heating, then small noise and drift.
  - Pressure: controlled ramp-up during compression, slight overshoot and hold, then release during ejection.
  - Adds random anomalies (pressure spikes/drops, temp glitches, short sensor “stuck” periods) to test alerting and visualization.
  - Yields per-second readings and occasional “quality inspection” data at the end of each cycle.

- [generate_idle.py](file:///d:/Riot%20Games/sem-8/molding_prototype/simulation/generate_idle.py)
  - A lightweight generator for live IDLE data only.
  - Writes one reading per second (temperature “breathing” around 30°C, tiny pressure) into SQLite.
  - Occasionally introduces small anomalies (blips and short flatlines) so the graph looks alive.
  - Intended to keep the dashboard animated without running full cycles.

## CS 102 (Data Structures & Logic)

- [state_machine.py](file:///d:/Riot%20Games/sem-8/molding_prototype/cs102/state_machine.py)
  - Minimal finite state machine defining allowed steps:
    - IDLE → HEATING → COMPRESSION → CURING → EJECTION → back to IDLE.
  - Validates transitions and reports the current state.

- [circular_buffer.py](file:///d:/Riot%20Games/sem-8/molding_prototype/cs102/circular_buffer.py)
  - Fixed-size ring buffer with constant-time append/get.
  - Used by the MQTT layer to temporarily store readings during network outages.

- [priority_queue.py](file:///d:/Riot%20Games/sem-8/molding_prototype/cs102/priority_queue.py)
  - Simple min-heap style priority queue implemented with a list.
  - Useful for processing critical alerts before minor ones.

- [hash_table.py](file:///d:/Riot%20Games/sem-8/molding_prototype/cs102/hash_table.py)
  - Basic hash table using buckets and a simple character-sum hash.
  - Used to store quick-look-up “recipes” (e.g., target temp/pressure/time) by name.

## CNDC (Communication & Network)

- [network_simulator.py](file:///d:/Riot%20Games/sem-8/molding_prototype/cndc/network_simulator.py)
  - Simulates connection outages and recoveries.
  - Lets the rest of the system test buffering and retransmission behavior.

- [mqtt_gateway.py](file:///d:/Riot%20Games/sem-8/molding_prototype/cndc/mqtt_gateway.py)
  - Publishes readings to an MQTT broker (paho-mqtt).
  - If the “network” is down, it buffers readings in a circular buffer.
  - On recovery, it flushes the buffer and resumes real-time publishing (QoS 1).
  - Also collects logs and sends them in batches periodically.

## MAT 101 (Physics-Based Models)

- [heat_transfer.py](file:///d:/Riot%20Games/sem-8/molding_prototype/mat101/heat_transfer.py)
  - Simple explicit finite-difference model of heat diffusion.
  - step(): advances the temperature distribution and returns the average plate temperature.
  - validate(): compares simulated sensor data to the model and saves a plot (with RMSE).

- [pressure_dynamics.py](file:///d:/Riot%20Games/sem-8/molding_prototype/mat101/pressure_dynamics.py)
  - Runge–Kutta (RK4) pressure model with basic pump/leak dynamics.
  - step(): advances pressure by a small timestep based on the differential equation.
  - validate(): compares simulated sensor data to the model and saves a plot (with RMSE).

## DBMS (Database)

- [db_connector.py](file:///d:/Riot%20Games/sem-8/molding_prototype/db/db_connector.py)
  - Opens / initializes the SQLite database and loads the schema.
  - Provides helper methods to insert readings and inspection results.
  - Offers simple query helpers for readings and alerts.
  - Ensures a default machine record exists.

---

How the pieces fit together:
- Data is generated by the simulators (either full cycles or idle) and written to the database (and optionally sent over MQTT).
- The dashboard reads the latest rows and plots them live, marking anomalies for quick attention.
- The orchestrator script ties these pieces into a complete “digital twin” prototype with validation and reporting.
