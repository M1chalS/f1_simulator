from simulation.car import Car
from simulation.track import Track
from simulation.simulator import Simulator
from physics import forces


def demo_corner_analysis():
    print("\n" + "="*80)
    print("DEMONSTRACJA: FIZYKA ZAKRĘTÓW")
    print("="*80 + "\n")

    car = Car()
    radii = [25, 40, 60, 100, 150]

    print("Maksymalne prędkości w zakrętach o różnych promieniach:\n")
    print(f"{'Promień [m]':<15} {'V_max [km/h]':<15} {'V_max [m/s]':<15} {'Docisk [N]':<15}")
    print("-" * 70)

    for r in radii:
        v_max = forces.max_corner_velocity(
            radius=r,
            tire_friction=car.tire_friction,
            mass=car.mass,
            lift_coefficient=car.lift_coefficient,
            frontal_area=car.frontal_area
        )
        df = forces.downforce(v_max, car.lift_coefficient, car.frontal_area)

        print(f"{r:<15} {v_max*3.6:<15.1f} {v_max:<15.1f} {df:<15.0f}")


def demo_braking():
    """Demonstracja hamowania."""
    print("\n" + "="*80)
    print("DEMONSTRACJA: HAMOWANIE")
    print("="*80 + "\n")

    car = Car()

    scenarios = [
        (350, 140, "Hamowanie przed ostrym zakrętem"),
        (300, 200, "Hamowanie przed średnim zakrętem"),
        (250, 180, "Hamowanie przed chicane"),
    ]

    print("Droga hamowania przy różnych prędkościach:\n")
    print(f"{'Scenariusz':<35} {'V_pocz':<12} {'V_docel':<12} {'Droga [m]':<12}")
    print("-" * 80)

    for v_init, v_final, desc in scenarios:
        v_i = v_init / 3.6  # konwersja km/h -> m/s
        v_f = v_final / 3.6

        dist = forces.braking_distance(
            initial_velocity=v_i,
            final_velocity=v_f,
            max_braking_force=car.max_braking_force,
            mass=car.mass,
            drag_coefficient=car.drag_coefficient,
            frontal_area=car.frontal_area
        )

        print(f"{desc:<35} {v_init:<12.0f} {v_final:<12.0f} {dist:<12.1f}")


def demo_track_comparison():
    """Porównanie charakterystyk torów."""
    print("\n" + "="*80)
    print("DEMONSTRACJA: PORÓWNANIE TORÓW")
    print("="*80 + "\n")

    tracks_info = [
        ("data/tracks.json", "Tor testowy"),
        ("data/monaco.json", "Monaco GP"),
        ("data/monza.json", "Monza GP"),
    ]

    car = Car()

    print(f"{'Tor':<25} {'Długość':<12} {'Czas':<10} {'V_max':<12} {'V_śr':<12} {'Segment/km':<12}")
    print("-" * 90)

    for track_path, name in tracks_info:
        try:
            track = Track.from_json(track_path)
            sim = Simulator(car, track, dt=0.01)
            result = sim.run()

            segments_per_km = len(track.segments) / (track.total_length / 1000)

            print(
                f"{name:<25} "
                f"{track.total_length:>8.0f} m   "
                f"{result.lap_time:>6.2f} s   "
                f"{result.max_velocity * 3.6:>6.1f} km/h   "
                f"{result.avg_velocity * 3.6:>6.1f} km/h   "
                f"{segments_per_km:>6.1f}"
            )
        except FileNotFoundError:
            print(f"{name:<25} [BRAK PLIKU]")

    print("\n💡 Segment/km = gęstość zakrętów (więcej = bardziej techniczny tor)")


def main():
    print("\n" + "🏎️ " * 26)
    print("SYMULATOR F1 - DEMONSTRACJA")
    print("🏎️ " * 26)

    demo_corner_analysis()
    demo_braking()
    demo_track_comparison()


if __name__ == "__main__":
    main()

