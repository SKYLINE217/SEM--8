import time

# CNDC Requirement: Simulate network fault tolerance
class NetworkSimulator:
    def __init__(self):
        self.connected = True
        self.outage_start_time = 0
        self.outage_duration = 0

    def simulate_outage(self, duration=30):
        print(f"[{time.strftime('%H:%M:%S')}] NETWORK OUTAGE DETECTED")
        self.connected = False
        self.outage_start_time = time.time()
        self.outage_duration = duration

    def check_status(self):
        if not self.connected:
            if time.time() - self.outage_start_time > self.outage_duration:
                self.connected = True
                print(f"[{time.strftime('%H:%M:%S')}] NETWORK RECOVERY")
        return self.connected
