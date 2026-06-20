#!/usr/bin/env python3

from simulation.car import Car
from simulation.track import Track
from simulation.simulator import Simulator

def test_braking_margin(car: Car, track: Track, margin: float, dt: float = 0.0005) -> dict:
    # Tymczasowo modyfikujemy simulator aby używał tego marginesu
    # (w produkcji można to dodać jako parametr do konstruktora)
    sim = Simulator(car, track, dt=dt)

    # Nadpisujemy metodę _simulate_straight aby używała naszego marginesu
    original_method = sim._simulate_straight

    def patched_simulate_straight(segment, telemetry, seg_index, state):
        # Kopiujemy oryginalną logikę ale z naszym marginesem
        segment_start = state["position"]
        segment_end = segment_start + segment.segment_length()

        corner_info = sim._get_next_corner_info(seg_index)

        braking_point = None
        target_velocity = None

        if corner_info is not None:
            from physics import forces, dynamics

            distance_to_corner, max_corner_v = corner_info
            current_v = state["velocity"]

            if current_v > max_corner_v:
                brake_dist = forces.braking_distance(
                    initial_velocity=current_v,
                    final_velocity=max_corner_v,
                    max_braking_force=car.max_braking_force,
                    mass=car.mass,
                    drag_coefficient=car.drag_coefficient,
                    frontal_area=car.frontal_area
                )

                # TUTAJ UŻYWAMY NASZEGO MARGINESU
                braking_point = segment_end + distance_to_corner - brake_dist * margin
                target_velocity = max_corner_v

        # Reszta bez zmian
        while state["position"] < segment_end:
            v = state["velocity"]

            from physics import forces, dynamics

            f_drag = forces.drag_force(
                v, car.drag_coefficient, car.frontal_area
            )
            f_downforce = forces.downforce(
                v, car.lift_coefficient, car.frontal_area
            )

            if braking_point is not None and state["position"] >= braking_point:
                if state.get("last_state") != "braking":
                    telemetry.record_braking_point(state["position"], v, target_velocity or 0.0)

                net_force = -(car.max_braking_force + f_drag)
                a = dynamics.acceleration(net_force, car.mass)
                vehicle_state = "braking"

                if target_velocity is not None and v <= target_velocity:
                    a = 0.0
                    vehicle_state = "coasting"
            else:
                f_traction = forces.traction_limit(
                    v, car.tire_friction, car.mass,
                    car.lift_coefficient, car.frontal_area
                )
                f_engine = forces.engine_force(v, car.engine_power, f_traction)
                net_force = f_engine - f_drag
                a = dynamics.acceleration(net_force, car.mass)
                vehicle_state = "accelerating"

            new_x, new_v = dynamics.integrate_step(
                state["position"], v, a, dt
            )
            state["position"] = new_x
            state["velocity"] = new_v
            state["time"] += dt
            state["last_state"] = vehicle_state

            telemetry.record(
                state["time"], state["position"], state["velocity"], a, seg_index,
                drag=f_drag, down=f_downforce, state=vehicle_state
            )

    sim._simulate_straight = patched_simulate_straight

    # Uruchom symulację
    result = sim.run()

    return {
        'margin': margin,
        'lap_time': result.lap_time,
        'max_velocity': result.max_velocity * 3.6,
        'avg_velocity': result.avg_velocity * 3.6,
        'braking_count': result.braking_count,
        'braking_distance': result.total_braking_distance,
        'braking_time': result.total_braking_time,
    }


def main():
    """Główna funkcja optymalizacji."""
    import argparse

    parser = argparse.ArgumentParser(description="Optymalizacja strategii hamowania")
    parser.add_argument("--track", type=str, default="data/monaco.json",
                       help="Ścieżka do pliku z torem")
    parser.add_argument("--aero-config", type=str, default="balanced",
                       choices=["high_downforce", "low_drag", "balanced"],
                       help="Konfiguracja aerodynamiczna")
    parser.add_argument("--min-margin", type=float, default=1.0,
                       help="Minimalny margines hamowania (domyślnie 1.0 = 100%%)")
    parser.add_argument("--max-margin", type=float, default=1.15,
                       help="Maksymalny margines hamowania (domyślnie 1.15 = 115%%)")
    parser.add_argument("--steps", type=int, default=16,
                       help="Liczba kroków do przetestowania")

    args = parser.parse_args()

    # Wczytaj tor
    track = Track.from_json(args.track)

    # Wybierz konfigurację
    if args.aero_config == "high_downforce":
        car = Car.high_downforce()
    elif args.aero_config == "low_drag":
        car = Car.low_drag()
    else:
        car = Car.balanced()

    print("=" * 80)
    print("OPTYMALIZACJA STRATEGII HAMOWANIA")
    print("=" * 80)
    print()
    print(f"📍 Tor: {track.name} ({track.total_length:.0f} m)")
    print(f"🏎️  Konfiguracja: {args.aero_config.upper().replace('_', ' ')}")
    print(f"   Cd={car.drag_coefficient:.2f}, CL={car.lift_coefficient:.2f}")
    print()
    print(f"🔧 Testowanie marginesów: {args.min_margin:.0%} - {args.max_margin:.0%}")
    print(f"   Liczba testów: {args.steps}")
    print()
    print("=" * 80)
    print()

    # Testuj różne marginesy
    margins = [args.min_margin + (args.max_margin - args.min_margin) * i / (args.steps - 1)
               for i in range(args.steps)]

    results = []

    print(f"{'Margines':<12} {'Czas [s]':<12} {'Różnica':<12} {'Hamowań':<10} {'Dystans [m]':<12}")
    print("-" * 80)

    best_time = float('inf')
    best_margin = None

    for margin in margins:
        print(f"Testowanie {margin:.0%}...", end="", flush=True)
        result = test_braking_margin(car, track, margin)
        results.append(result)

        if result['lap_time'] < best_time:
            best_time = result['lap_time']
            best_margin = margin

        diff = result['lap_time'] - best_time
        marker = " 🏆" if margin == best_margin else ""

        print(f"\r{margin:>10.0%}  {result['lap_time']:<12.3f} {diff:>+11.3f}  "
              f"{result['braking_count']:<10} {result['braking_distance']:<12.1f}{marker}")

    print()
    print("=" * 80)
    print("PODSUMOWANIE")
    print("=" * 80)
    print()
    print(f"🏆 NAJLEPSZY MARGINES: {best_margin:.0%}")
    print(f"   Czas okrążenia:     {best_time:.3f} s")
    print()

    # Dodatkowa analiza
    worst_time = max(r['lap_time'] for r in results)
    time_span = worst_time - best_time

    print(f"📊 Zakres czasów:       {time_span:.3f} s ({time_span/best_time*100:.1f}% różnicy)")
    print(f"   Najszybszy:          {best_time:.3f} s")
    print(f"   Najwolniejszy:       {worst_time:.3f} s")
    print()

    # Sprawdź czy margines ma duży wpływ
    if time_span < 0.1:
        print("💡 WNIOSEK: Margines hamowania ma MINIMALNY wpływ na czas okrążenia (<0.1s)")
        print("   → Można bezpiecznie używać większego marginesu")
    elif time_span < 0.5:
        print("💡 WNIOSEK: Margines hamowania ma UMIARKOWANY wpływ na czas okrążenia (<0.5s)")
        print(f"   → Optymalny margines: {best_margin:.0%}")
    else:
        print("💡 WNIOSEK: Margines hamowania ma ZNACZĄCY wpływ na czas okrążenia (>0.5s)")
        print(f"   → Optymalny margines: {best_margin:.0%} (krytyczny dla osiągów!)")
    print()

    # Bezpieczeństwo vs wydajność
    safe_margin = max(margins)
    safe_result = next(r for r in results if r['margin'] == safe_margin)
    safety_cost = safe_result['lap_time'] - best_time

    print(f"⚖️  BEZPIECZEŃSTWO vs WYDAJNOŚĆ:")
    print(f"   Najbezpieczniejszy margines ({safe_margin:.0%}): {safe_result['lap_time']:.3f} s")
    print(f"   Koszt bezpieczeństwa: +{safety_cost:.3f} s ({safety_cost/best_time*100:.2f}%)")
    print()

    recommended = best_margin + 0.03  # +3% dla bezpieczeństwa
    if recommended > args.max_margin:
        recommended = best_margin

    print(f"✅ REKOMENDACJA: Margines {recommended:.0%}")
    print(f"   (optymalny {best_margin:.0%} + 3% dla bezpieczeństwa)")


if __name__ == "__main__":
    main()

