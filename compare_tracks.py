from simulation.car import Car
from simulation.track import Track
from simulation.simulator import Simulator

def simulate_track(track_path: str, dt: float = 0.01):
    car = Car()
    track = Track.from_json(track_path)
    sim = Simulator(car, track, dt=dt)
    result = sim.run()
    return track, result


def main():
    tracks = [
        "data/tracks.json",
        "data/monaco.json",
        "data/monza.json"
    ]

    print("=" * 80)
    print("PORÓWNANIE WYNIKÓW SYMULACJI NA RÓŻNYCH TORACH")
    print("=" * 80)
    print()

    results = []

    for track_path in tracks:
        try:
            track, result = simulate_track(track_path)
            results.append((track, result))
        except FileNotFoundError:
            print(f"Plik {track_path} nie istnieje, pomijam...")
            continue

    # Tabela wyników
    print(f"{'Tor':<25} {'Długość':<12} {'Czas':<10} {'V_max':<12} {'V_śr':<12}")
    print("-" * 80)

    for track, result in results:
        print(
            f"{track.name:<25} "
            f"{track.total_length:>8.0f} m   "
            f"{result.lap_time:>6.2f} s   "
            f"{result.max_velocity * 3.6:>6.1f} km/h   "
            f"{result.avg_velocity * 3.6:>6.1f} km/h"
        )

    print()
    print("=" * 80)
    print()

    # Szczegóły dla każdego toru
    for track, result in results:
        print(f"Tor:  {track.name}")
        print(f"      Liczba segmentów: {len(track.segments)}")
        print(f"      Długość toru: {track.total_length:.1f} m")
        print()
        print(f"      {result.summary()}")
        print()

        corners = [s for s in track.segments if s.type == "corner"]
        if corners:
            radii = [c.radius for c in corners if c.radius]
            if radii:
                print(f"    Zakręty:")
                print(f"      - Liczba: {len(corners)}")
                print(f"      - Promień min: {min(radii)} m")
                print(f"      - Promień max: {max(radii)} m")
                print(f"      - Promień śr: {sum(radii)/len(radii):.1f} m")
        print()
        print("-" * 80)
        print()


if __name__ == "__main__":
    main()

