import numpy as np
import matplotlib.pyplot as plt

# MAT 101 Requirement: Pressure dynamics solver: RK4 method
class PressureDynamicsSolver:
    def __init__(self, target_pressure=150):
        self.P = 0
        self.target = target_pressure
        self.Qp = 5.0 # Pump flow parameter (tuned for 150 bar in ~8s)
        self.C = 0.1  # Hydraulic capacitance
        self.leakage = 0.002

    def derivative(self, P):
        # dP/dt = (Qp - 0.002P)/C
        # Control logic: if P >= target, Qp drops to maintain
        flow = self.Qp if P < self.target else self.leakage * P 
        return (flow - self.leakage * P) / self.C

    def step(self, dt=1.0):
        # RK4 Implementation
        k1 = self.derivative(self.P)
        k2 = self.derivative(self.P + 0.5 * dt * k1)
        k3 = self.derivative(self.P + 0.5 * dt * k2)
        k4 = self.derivative(self.P + dt * k3)
        
        self.P = self.P + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
        return self.P

    def validate(self, simulated_data, filename="pressure_validation.png"):
        time_points = np.arange(len(simulated_data))
        model_pressures = []
        
        # Reset for validation
        self.P = 0
        
        for _ in time_points:
            model_pressures.append(self.step(1.0))
            
        plt.figure()
        plt.plot(time_points, simulated_data, label='Simulated Sensor')
        plt.plot(time_points, model_pressures, label='Mathematical Model', linestyle='--')
        
        rmse = np.sqrt(np.mean((np.array(simulated_data) - np.array(model_pressures))**2))
        plt.title(f'Pressure Dynamics Validation (RMSE: {rmse:.2f})')
        plt.legend()
        plt.savefig(filename)
        print(f"Pressure Validation Plot saved to {filename}. RMSE: {rmse}")
        return rmse
