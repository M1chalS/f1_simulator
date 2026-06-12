from __future__ import annotations

import argparse
from pathlib import Path

from simulation.car import Car
from simulation.simulator import Simulator
from simulation.track import Track

DEFAULT_TRACK = Path(__file__).parent / "data" / "tracks.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Symulator okrążenia bolidu F1")
    parser.add_argument(
        "--track", type=str, default=str(DEFAULT_TRACK),
        help="Ścieżka do pliku JSON z definicją toru.",
    )
    parser.add_argument(
        "--dt", type=float, default=0.01,
        help="Krok czasowy symulacji [s].",
    )
    parser.add_argument(
        "--aero-config", type=str, default="balanced",
        choices=["high_downforce", "low_drag", "balanced"],
        help="Konfiguracja aerodynamiczna: high_downforce (Monaco), low_drag (Monza), balanced (default).",
    )
    parser.add_argument(
        "--no-plot", action="store_true",
        help="Nie wyświetlaj wykresów telemetrii.",
    )
    parser.add_argument(
        "--show-aero", action="store_true",
        help="Pokaż dodatkowe wykresy sił aerodynamicznych.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Wybór konfiguracji aerodynamicznej
    if args.aero_config == "high_downforce":
        car = Car.high_downforce()
        print(f"Konfiguracja: HIGH DOWNFORCE")
    elif args.aero_config == "low_drag":
        car = Car.low_drag()
        print(f"Konfiguracja: LOW DRAG")
    else:
        car = Car.balanced()
        print(f"Konfiguracja: BALANCED")
    
    print(f"  Cd={car.drag_coefficient:.2f}, CL={car.lift_coefficient:.2f}\n")
    
    track = Track.from_json(args.track)

    print(f"Tor: {track.name}")
    print(f"Liczba segmentów: {len(track)}")
    print(f"Całkowita długość toru: {track.total_length:.1f} m\n")

    simulator = Simulator(car=car, track=track, dt=args.dt)
    result = simulator.run()

    print(result.summary())

    if not args.no_plot:
        try:
            from visualization.plots import plot_telemetry, plot_aerodynamics
            plot_telemetry(result.telemetry)
            
            if args.show_aero:
                plot_aerodynamics(result.telemetry)
        except ImportError:
            print("\n[Uwaga] matplotlib nie jest zainstalowany — pomijam wykresy.")


if __name__ == "__main__":
    main()

