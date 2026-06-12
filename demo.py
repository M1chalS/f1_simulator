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


def demo_aerodynamics():
    """Demonstracja wpływu aerodynamiki (Etap 3)."""
    print("\n" + "="*80)
    print("DEMONSTRACJA: AERODYNAMIKA I KONFIGURACJE")
    print("="*80 + "\n")

    # 3 konfiguracje aerodynamiczne
    configs = [
        ("HIGH DOWNFORCE 🏔️", Car.high_downforce()),
        ("BALANCED ⚖️", Car.balanced()),
        ("LOW DRAG 🚀", Car.low_drag()),
    ]

    # Testuj na dwóch torach
    tracks_to_test = [
        ("data/monaco.json", "Monaco GP (techniczny - dużo zakrętów)"),
        ("data/monza.json", "Monza GP (szybki - długie proste)"),
    ]

    for track_path, track_description in tracks_to_test:
        try:
            track = Track.from_json(track_path)
        except FileNotFoundError:
            print(f"⚠️  Plik {track_path} nie istnieje - pomijam")
            continue

        print(f"📍 {track_description}")
        print(f"   Długość: {track.total_length:.1f} m")

        # Analiza toru
        corners = [s for s in track.segments if s.type == "corner"]
        straights = [s for s in track.segments if s.type == "straight"]
        total_straight_length = sum(s.length for s in straights)
        print(f"   Proste: {len(straights)} ({total_straight_length:.0f} m), Zakręty: {len(corners)}\n")

        print(f"{'Konfiguracja':<25} {'Cd':<8} {'CL':<8} {'Czas':<10} {'V_max':<12} {'Max Down':<12}")
        print("-" * 80)

        results = []
        for name, car in configs:
            sim = Simulator(car=car, track=track, dt=0.01)
            result = sim.run()
            results.append((name, result))

            print(
                f"{name:<25} "
                f"{car.drag_coefficient:<8.2f} "
                f"{car.lift_coefficient:<8.2f} "
                f"{result.lap_time:<10.2f} "
                f"{result.max_velocity * 3.6:<12.1f} "
                f"{result.max_downforce:<12.0f}"
            )

        # Znajdź najszybszy
        fastest_idx = min(range(len(results)), key=lambda i: results[i][1].lap_time)
        fastest_name, fastest_result = results[fastest_idx]

        print(f"\n🏆 NAJSZYBSZY: {fastest_name} ({fastest_result.lap_time:.2f} s)")
        print("\nRÓŻNICE CZASOWE:")
        for name, result in results:
            delta = result.lap_time - fastest_result.lap_time
            emoji = "🏆" if delta == 0 else "  "
            print(f"{emoji} {name:25s} +{delta:.2f} s")

        print()

    print("="*80)
    print("💡 ANALIZA:")
    print("   • Cd = opór aerodynamiczny (niższy = większa V-max na prostych)")
    print("   • CL = docisk aerodynamiczny (wyższy = szybsze przejazdy przez zakręty)")
    print("   • Monaco: dużo ostrych zakrętów → HIGH DOWNFORCE wygrywa!")
    print("   •  Monza: bardzo długie proste → LOW DRAG zdecydowanie najlepszy")
    print("   • Setup ma OGROMNY wpływ - różnica nawet kilka sekund!")
    print("="*80)


def main():
    print("\n" + "🏎️ " * 26)
    print("SYMULATOR F1 - DEMONSTRACJA")
    print("🏎️ " * 26)

    demo_corner_analysis()
    demo_braking()
    demo_track_comparison()
    demo_aerodynamics()

    print("\n" + "="*80)
    print("✅ DEMONSTRACJA ZAKOŃCZONA")
    print("="*80)


if __name__ == "__main__":
    main()

