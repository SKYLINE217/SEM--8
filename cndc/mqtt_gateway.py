import json
import time
import paho.mqtt.client as mqtt
from cs102.circular_buffer import CircularBuffer

# CNDC Requirement: MQTT publisher/subscriber using paho-mqtt with TLS simulation
# CNDC Requirement: Dual-channel transmission: real-time (QoS 1) + batch historical logs every 60 sec
class MQTTGateway:
    def __init__(self, network_sim, buffer_size=100):
        self.network_sim = network_sim
        self.buffer = CircularBuffer(buffer_size)
        self.client = mqtt.Client(client_id="molding_machine_01")
        # TLS Simulation (Conceptual)
        self.client.tls_set_context(context=None) 
        self.batch_logs = []
        self.last_batch_time = time.time()

    def connect(self, broker="test.mosquitto.org", port=1883):
        try:
            # We use a public broker for demonstration, or localhost
            # If connection fails, we just proceed (as we are simulating the network layer logic mostly)
            self.client.connect(broker, port, 60)
            self.client.loop_start()
        except Exception as e:
            print(f"MQTT Connection warning: {e} (Proceeding in simulation mode)")

    def publish_reading(self, reading):
        payload = json.dumps(reading)
        
        # Check network status from simulator
        is_connected = self.network_sim.check_status()

        if is_connected:
            # Flush buffer if any
            while not self.buffer.is_empty():
                buffered_item = self.buffer.get()
                print(f"[{time.strftime('%H:%M:%S')}] Retransmitting buffered data...")
                self.client.publish("molding/sensors", json.dumps(buffered_item), qos=1)
            
            # Send current data
            self.client.publish("molding/sensors", payload, qos=1)
        else:
            # Buffer data
            print(f"[{time.strftime('%H:%M:%S')}] Buffering reading...")
            self.buffer.append(reading)

        # Batch handling
        self.batch_logs.append(reading)
        if time.time() - self.last_batch_time > 60:
            self._send_batch()

    def _send_batch(self):
        if self.network_sim.check_status():
            payload = json.dumps(self.batch_logs)
            self.client.publish("molding/batch_logs", payload, qos=1)
            self.batch_logs = []
            self.last_batch_time = time.time()

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()
