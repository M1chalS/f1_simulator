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

