-- DBMS Layer Requirement: Create 4 tables with referential integrity
CREATE TABLE IF NOT EXISTS machines (
    machine_id INTEGER PRIMARY KEY,
    machine_name TEXT
);

CREATE TABLE IF NOT EXISTS sensor_readings (
    reading_id INTEGER PRIMARY KEY AUTOINCREMENT,
    machine_id INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    platen_temp_upper REAL,
    platen_temp_lower REAL,
    hydraulic_pressure REAL,
    cycle_state TEXT,
    FOREIGN KEY(machine_id) REFERENCES machines(machine_id)
);

CREATE TABLE IF NOT EXISTS quality_inspection (
    inspection_id INTEGER PRIMARY KEY AUTOINCREMENT,
    reading_id INTEGER,
    density REAL,
    hardness_shore_a REAL,
    visual_defects INTEGER,
    FOREIGN KEY(reading_id) REFERENCES sensor_readings(reading_id)
);

CREATE TABLE IF NOT EXISTS alerts (
    alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
    machine_id INTEGER,
    type TEXT,
    severity TEXT,
    resolved BOOLEAN DEFAULT 0,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(machine_id) REFERENCES machines(machine_id)
);

-- DBMS Layer Requirement: Implement 1 trigger: Auto-insert CRITICAL alert when hydraulic_pressure > 190
CREATE TRIGGER IF NOT EXISTS check_pressure_critical
AFTER INSERT ON sensor_readings
WHEN new.hydraulic_pressure > 190
BEGIN
    INSERT INTO alerts (machine_id, type, severity, resolved, timestamp)
    VALUES (new.machine_id, 'High Pressure Alert', 'CRITICAL', 0, new.timestamp);
END;

-- DBMS Layer Requirement: Create 1 materialized view (View in SQLite)
CREATE VIEW IF NOT EXISTS daily_quality_summary AS
SELECT 
    DATE(sr.timestamp) as date,
    AVG(qi.density) as avg_density,
    AVG(qi.hardness_shore_a) as avg_hardness,
    SUM(qi.visual_defects) as total_defects
FROM sensor_readings sr
JOIN quality_inspection qi ON sr.reading_id = qi.reading_id
GROUP BY DATE(sr.timestamp);
