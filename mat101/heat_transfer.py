import numpy as np
import matplotlib.pyplot as plt

# MAT 101 Requirement: Heat transfer solver: Explicit finite difference
class HeatTransferSolver:
    def __init__(self, alpha=1.2e-7, L=0.05, T_target=165, T_init=25, nx=20):
        self.alpha = alpha
        self.L = L  # Thickness in meters
        self.nx = nx
        self.dx = L / (nx - 1)
        self.T = np.ones(nx) * T_init
        self.T_target = T_target
        # Stability condition: dt <= dx^2 / (2*alpha)
        self.dt = 0.5 * (self.dx**2) / (2 * alpha)
    
    def step(self, duration=1.0):
        steps = int(duration / self.dt)
        for _ in range(steps):
            T_new = self.T.copy()
            # Boundary conditions: Top and Bottom heated to target
            self.T[0] = self.T_target
            self.T[-1] = self.T_target
            
            for i in range(1, self.nx - 1):
                T_new[i] = self.T[i] + self.alpha * self.dt / self.dx**2 * (self.T[i+1] - 2*self.T[i] + self.T[i-1])
            self.T = T_new
        return np.mean(self.T) # Return average temp of the plate

    def validate(self, simulated_data, filename="heat_validation.png"):
        time_points = np.arange(len(simulated_data))
        model_temps = []
        
        # Reset for validation run
        temp_solver = HeatTransferSolver() 
        for _ in time_points:
            model_temps.append(temp_solver.step(1.0)) # 1 sec steps
            
        plt.figure()
        plt.plot(time_points, simulated_data, label='Simulated Sensor')
        plt.plot(time_points, model_temps, label='Mathematical Model', linestyle='--')
        
        # Calculate RMSE
        rmse = np.sqrt(np.mean((np.array(simulated_data) - np.array(model_temps))**2))
        plt.title(f'Heat Transfer Validation (RMSE: {rmse:.2f})')
        plt.legend()
        plt.savefig(filename)
        print(f"Heat Transfer Validation Plot saved to {filename}. RMSE: {rmse}")
        return rmse
