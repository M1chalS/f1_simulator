from __future__ import annotations

from simulation.simulator import Telemetry

# Rysuje wykresy prędkości, przyspieszenia i pozycji.
def plot_telemetry(telemetry: Telemetry, show: bool = True,
                   save_path: str | None = None) -> None:
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(3, 1, figsize=(10, 9), sharex=False)

    # Prędkość vs czas (w km/h dla czytelności)
    velocity_kmh = [v * 3.6 for v in telemetry.velocity]
    axes[0].plot(telemetry.time, velocity_kmh, color="tab:blue")
    axes[0].set_xlabel("Czas [s]")
    axes[0].set_ylabel("Prędkość [km/h]")
    axes[0].set_title("Prędkość w czasie")
    axes[0].grid(True, alpha=0.3)

    # Przyspieszenie vs czas
    axes[1].plot(telemetry.time, telemetry.acceleration, color="tab:red")
    axes[1].set_xlabel("Czas [s]")
    axes[1].set_ylabel("Przyspieszenie [m/s²]")
    axes[1].set_title("Przyspieszenie w czasie")
    axes[1].grid(True, alpha=0.3)

    # Prędkość vs pozycja na torze
    axes[2].plot(telemetry.position, velocity_kmh, color="tab:green")
    axes[2].set_xlabel("Pozycja na torze [m]")
    axes[2].set_ylabel("Prędkość [km/h]")
    axes[2].set_title("Prędkość w funkcji pozycji")
    axes[2].grid(True, alpha=0.3)

    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=120)
    if show:
        plt.show()
    plt.close(fig)

# Drag, downforce i stan pojazdu vs pozycja na torze
def plot_aerodynamics(telemetry: Telemetry, show: bool = True,
                      save_path: str | None = None) -> None:
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    
    # Siły aerodynamiczne vs pozycja
    drag_kn = [f / 1000.0 for f in telemetry.drag_force]  # w kN
    down_kn = [f / 1000.0 for f in telemetry.downforce]   # w kN
    
    axes[0].plot(telemetry.position, drag_kn, color="tab:orange", label="Drag Force", linewidth=1.5)
    axes[0].plot(telemetry.position, down_kn, color="tab:purple", label="Downforce", linewidth=1.5)
    axes[0].set_ylabel("Siła [kN]")
    axes[0].set_title("Siły aerodynamiczne wzdłuż toru")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Prędkość i stan pojazdu
    velocity_kmh = [v * 3.6 for v in telemetry.velocity]
    axes[1].plot(telemetry.position, velocity_kmh, color="tab:blue", linewidth=1.5)
    axes[1].set_xlabel("Pozycja na torze [m]")
    axes[1].set_ylabel("Prędkość [km/h]")
    axes[1].set_title("Prędkość wzdłuż toru")
    axes[1].grid(True, alpha=0.3)
    
    state_colors = {
        "accelerating": "lightgreen",
        "braking": "lightcoral",
        "cornering": "lightyellow",
        "cornering_accel": "khaki",
        "cornering_brake": "lightpink",
        "coasting": "lightgray"
    }
    
    if telemetry.state:
        current_state = telemetry.state[0]
        start_pos = telemetry.position[0]
        
        for i in range(1, len(telemetry.state)):
            if telemetry.state[i] != current_state or i == len(telemetry.state) - 1:
                end_pos = telemetry.position[i]
                color = state_colors.get(current_state, "white")
                axes[1].axvspan(start_pos, end_pos, alpha=0.2, color=color)
                
                current_state = telemetry.state[i]
                start_pos = end_pos
    
    fig.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=120)
    if show:
        plt.show()
    plt.close(fig)
