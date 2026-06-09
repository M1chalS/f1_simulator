from __future__ import annotations

import argparse
from pathlib import Path

from simulation.car import Car
from simulation.simulator import Simulator
from simulation.track import Track

DEFAULT_TRACK = Path(__file__).parent / "data" / "tracks.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Symulator okrążenia bolidu F1 (Etap 1)")
    parser.add_argument(
        "--track", type=str, default=str(DEFAULT_TRACK),
        help="Ścieżka do pliku JSON z definicją toru.",
    )
    parser.add_argument(
        "--dt", type=float, default=0.01,
        help="Krok czasowy symulacji [s].",
    )
    parser.add_argument(
        "--no-plot", action="store_true",
        help="Nie wyświetlaj wykresów telemetrii.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    car = Car()
    track = Track.from_json(args.track)

    print(f"Tor: {track.name}")
    print(f"Liczba segmentów: {len(track)}")
    print(f"Całkowita długość toru: {track.total_length:.1f} m\n")

    simulator = Simulator(car=car, track=track, dt=args.dt)
    result = simulator.run()

    print(result.summary())

    if not args.no_plot:
        try:
            from visualization.plots import plot_telemetry
            plot_telemetry(result.telemetry)
        except ImportError:
            print("\n[Uwaga] matplotlib nie jest zainstalowany — pomijam wykresy.")


if __name__ == "__main__":
    main()

