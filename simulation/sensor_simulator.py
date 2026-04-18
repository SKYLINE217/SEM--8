import random
import time
import math
from cs102.state_machine import StateMachine

class SensorSimulator:
    def __init__(self, machine_id=1, cycle_duration=180):
        self.machine_id = machine_id
        self.state_machine = StateMachine()
        self.cycle_duration = cycle_duration
        self.time_in_cycle = 0
        self.cycle_count = 0
        self.base_temp = 25
        self.base_pressure = 0
        self.target_temp = 165
        self.target_pressure = 150
        self.last_temp = self.base_temp
        self.last_pressure = self.base_pressure
        self.anomaly_events = []

    def _schedule_anomalies(self):
        self.anomaly_events = []
        if random.random() < 0.3:
            start = random.randint(40, 120)
            duration = random.randint(2, 5)
            self.anomaly_events.append({"type": "pressure_spike", "start": start, "end": start + duration})
        if random.random() < 0.2:
            start = random.randint(60, 150)
            duration = random.randint(2, 6)
            self.anomaly_events.append({"type": "pressure_drop", "start": start, "end": start + duration})
        if random.random() < 0.25:
            start = random.randint(20, 170)
            duration = random.randint(1, 3)
            sign = 1 if random.random() < 0.5 else -1
            amp = random.uniform(25, 40) * sign
            self.anomaly_events.append({"type": "temp_glitch", "start": start, "end": start + duration, "amp": amp})
        if random.random() < 0.15:
            start = random.randint(30, 160)
            duration = random.randint(5, 10)
            target = random.choice(["temp", "pressure"])
            self.anomaly_events.append({"type": "stuck", "start": start, "end": start + duration, "target": target})

    def _apply_anomalies(self):
        for ev in self.anomaly_events:
            if ev["start"] <= self.time_in_cycle < ev["end"]:
                if ev["type"] == "pressure_spike":
                    self.base_pressure = max(self.base_pressure, random.uniform(200, 220))
                elif ev["type"] == "pressure_drop":
                    self.base_pressure = min(self.base_pressure, random.uniform(0, 15))
                elif ev["type"] == "temp_glitch":
                    self.base_temp = self.base_temp + ev["amp"]
                elif ev["type"] == "stuck":
                    if ev["target"] == "temp":
                        self.base_temp = self.last_temp
                    else:
                        self.base_pressure = self.last_pressure

    def generate_cycle_data(self, total_cycles=10):
        for cycle in range(1, total_cycles + 1):
            self.cycle_count = cycle
            self.time_in_cycle = 0
            self.state_machine.transition("HEATING")
            self._schedule_anomalies()

            while self.time_in_cycle < self.cycle_duration:
                if self.time_in_cycle == 10:
                    self.state_machine.transition("COMPRESSION")
                elif self.time_in_cycle == 150:
                    self.state_machine.transition("CURING")
                elif self.time_in_cycle == 170:
                    self.state_machine.transition("EJECTION")
                elif self.time_in_cycle == 179:
                    self.state_machine.transition("IDLE")

                if self.state_machine.get_state() == "HEATING":
                    tau = 15
                    self.base_temp = self.target_temp - (self.target_temp - self.base_temp) * math.exp(-1 / tau)
                else:
                    noise = random.gauss(0, 2.5)
                    drift = (self.cycle_count * 0.3 / 60)
                    self.base_temp = self.target_temp + noise - drift

                if self.state_machine.get_state() == "COMPRESSION":
                    ramp = min(self.target_pressure, self.base_pressure + max(10, 25 - self.base_pressure * 0.05))
                    self.base_pressure = ramp
                    if self.base_pressure >= self.target_pressure:
                        noise = random.gauss(0, 6)
                        overshoot = random.uniform(0, 5)
                        self.base_pressure = self.target_pressure + noise + overshoot
                elif self.state_machine.get_state() == "CURING":
                    noise = random.gauss(0, 4)
                    self.base_pressure = self.target_pressure + noise
                elif self.state_machine.get_state() == "EJECTION":
                    self.base_pressure = max(0, self.base_pressure - 30)

                self._apply_anomalies()

                reading = {
                    "machine_id": self.machine_id,
                    "timestamp": time.time(),
                    "platen_temp_upper": round(self.base_temp, 2),
                    "platen_temp_lower": round(self.base_temp - 2, 2),
                    "hydraulic_pressure": round(self.base_pressure, 2),
                    "cycle_state": self.state_machine.get_state()
                }

                inspection = None
                if self.time_in_cycle == self.cycle_duration - 1:
                    temp_diff = self.target_temp - self.base_temp
                    density_loss = (max(0, temp_diff) / 5) * 0.02
                    base_density = 2.5
                    density = base_density - density_loss + random.gauss(0, 0.01)
                    inspection = {
                        "density": round(density, 3),
                        "hardness_shore_a": round(90 + random.gauss(0, 2), 1),
                        "visual_defects": 1 if random.random() < 0.1 else 0
                    }

                yield reading, inspection
                self.last_temp = self.base_temp
                self.last_pressure = self.base_pressure
                self.time_in_cycle += 1
                time.sleep(0.05)
