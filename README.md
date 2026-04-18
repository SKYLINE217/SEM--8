# IoT-Enabled Compression Molding Machine Prototype

This project is a comprehensive digital twin prototype for a 4-pillar rubber compression molding machine. It demonstrates the integration of embedded systems, network communication, data structures, mathematical modeling, and real-time visualization to monitor and control the manufacturing process.

## 🏗 System Architecture & Module Breakdown

This prototype is built on four core academic pillars, each solving a specific engineering challenge in the data flow:

### 1. CNDC (Communication & Network Data Communication)
**Role:** The Nervous System
*   **Purpose:** Handles the transmission of sensor data from the machine (edge) to the server (cloud/local DB).
*   **Key Components:**
    *   **MQTT Gateway:** Simulates a lightweight publish-subscribe messaging protocol standard in IoT.
    *   **Network Simulator:** Deliberately injects faults (latency, packet loss, connection drops) to test system resilience.
    *   **Reliability:** Implements **QoS 1 (At Least Once)** delivery to ensure no critical pressure or temperature readings are lost during transmission.

### 2. CS 102 (Data Structures & Algorithms)
**Role:** The Brain (Logic & Efficiency)
*   **Purpose:** Manages data efficiently in memory before it hits the database or display.
*   **Key Implementations:**
    *   **Circular Buffer (O(1)):** Acts as a temporary cache during network outages. If the connection drops, data loops here until connectivity is restored, preventing data loss.
    *   **State Machine:** Formally defines the machine's lifecycle (`IDLE` -> `CLOSING` -> `CURING` -> `OPENING` -> `EJECTING`) to ensure valid transitions and logic.
    *   **Priority Queue (Heap):** Manages Alerts. Critical errors (e.g., "Seal Rupture") are processed before Warnings (e.g., "Maintenance Due"), regardless of arrival time.
    *   **Hash Table:** Stores production recipes (Setpoints for Temp/Pressure) for O(1) instant lookup during cycle initialization.

### 3. MAT 101 (Mathematical Modeling)
**Role:** The Physics Engine
*   **Purpose:** Generates realistic data behavior and validates sensor readings against physical laws.
*   **Key Models:**
    *   **Heat Transfer (Finite Difference):** Simulates how heat diffuses through the rubber mold over time, rather than just randomizing numbers.
    *   **Pressure Dynamics (Runge-Kutta 4):** Solves differential equations to model the hydraulic system's pressure ramp-up, providing a smooth, realistic curve.
    *   **Validation:** The system compares "Sensor" readings against these "Math Models" to detect anomalies (e.g., if a sensor says 200°C but physics says it should be 150°C, it's a sensor fault).

### 4. DBMS (Database Management System)
**Role:** The Memory (Storage & Persistence)
*   **Purpose:** Persists historical data, configuration, and audit logs.
*   **Key Components:**
    *   **Schema:** Normalized tables for `machines`, `sensor_readings`, `quality_inspection`, and `alerts`.
    *   **Triggers:** Automatic logic that fires on data insertion (e.g., `IF pressure > 190 THEN INSERT INTO alerts`).
    *   **Materialized Views:** Pre-aggregated summaries for daily quality reports to speed up dashboard queries.

---

## 🔄 The Data Flow Pipeline

How data moves through the system:

1.  **Generation (Simulation/MAT 101):**
    *   The `simulation/` scripts use **MAT 101** physics models to generate raw Temperature and Pressure values based on the current machine state.
    *   Real-time idle data is generated with organic noise (sine waves) to mimic live sensors.

2.  **Buffering & Logic (CS 102):**
    *   Data enters the **State Machine** to tag it with the correct cycle phase.
    *   If the network is down, data is pushed into the **Circular Buffer**.
    *   If an anomaly is detected, it's pushed to the **Priority Queue** of alerts.

3.  **Transmission (CNDC):**
    *   The **MQTT Gateway** picks up data. It simulates network conditions (lag/jitter).
    *   Upon successful transmission, the local buffer is flushed.

4.  **Storage (DBMS):**
    *   Data lands in the SQLite database.
    *   **Triggers** instantly analyze the incoming stream for safety violations (e.g., Overpressure).

5.  **Visualization (Dashboard):**
    *   The Streamlit app queries the **DBMS**.
    *   It renders the real-time graph (using `timestamp ASC` sorting) and animates the hydraulic pillars based on the latest pressure values.

---

## 🚀 How to Run

### Prerequisites
*   Python 3.8+
*   Dependencies: `pip install -r requirements.txt`

### 1. Run the Real-Time Simulation
This script generates continuous "live" data, resolves critical alerts, and keeps the dashboard animated.

```bash
python simulation/generate_idle.py
```

### 2. Launch the Dashboard
Open a new terminal and run:

```bash
python -m streamlit run dashboard/app.py
```

### 3. (Optional) Run Full Batch Prototype
To see the batch simulation with statistical analysis and outage recovery tests:

```bash
python run_prototype.py
```
