from __future__ import annotations

import argparse

from simulation.car import Car
from simulation.simulator import Simulator
from simulation.track import Track

# Porównuje 3 konfiguracje aerodynamiczne na danym torze.
def compare_aero_configs(track_path: str, dt: float = 0.01) -> None:
    track = Track.from_json(track_path)
    print(f"{'='*70}")
    print(f"TOR: {track.name}")
    print(f"Długość: {track.total_length:.1f} m ({track.total_length/1000:.3f} km)")
    print(f"{'='*70}\n")
    
    configs = [
        ("HIGH DOWNFORCE", Car.high_downforce()),
        ("BALANCED", Car.balanced()),
        ("LOW DRAG", Car.low_drag()),
    ]
    
    results = []
    
    for config_name, car in configs:
        simulator = Simulator(car=car, track=track, dt=dt)
        result = simulator.run()
        
        results.append({
            "name": config_name,
            "car": car,
            "result": result
        })
        
        print(f"\n{config_name}")
        print(f"{'-'*70}")
        print(f"  Cd={car.drag_coefficient:.2f}, CL={car.lift_coefficient:.2f}")
        print(f"  Czas okrążenia:      {result.lap_time:.3f} s")
        print(f"  Prędkość max:        {result.max_velocity * 3.6:.1f} km/h")
        print(f"  Prędkość średnia:    {result.avg_velocity * 3.6:.1f} km/h")
        print(f"  Max downforce:       {result.max_downforce:.0f} N")
        print(f"  Avg downforce:       {result.avg_downforce:.0f} N")
        print(f"  Max drag:            {result.max_drag:.0f} N")
        print(f"  Avg drag:            {result.avg_drag:.0f} N")
    
    # Podsumowanie
    print(f"\n{'='*70}")
    print("PODSUMOWANIE")
    print(f"{'='*70}")
    
    best_time_idx = min(range(len(results)), key=lambda i: results[i]["result"].lap_time)
    fastest_idx = max(range(len(results)), key=lambda i: results[i]["result"].max_velocity)
    
    print(f"\nNajszybszy czas:     {results[best_time_idx]['name']}")
    print(f"                     {results[best_time_idx]['result'].lap_time:.3f} s")
    
    print(f"\nNajwyższa V-max:     {results[fastest_idx]['name']}")
    print(f"                     {results[fastest_idx]['result'].max_velocity * 3.6:.1f} km/h")
    
    # Różnice czasowe
    print(f"\nRóżnice czasowe względem najszybszego:")
    best_time = results[best_time_idx]["result"].lap_time
    for res in results:
        delta = res["result"].lap_time - best_time
        print(f"  {res['name']:30s} +{delta:.3f} s")
    
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Porównanie konfiguracji aerodynamicznych"
    )
    parser.add_argument(
        "track", type=str, help="Ścieżka do pliku JSON z torem"
    )
    parser.add_argument(
        "--dt", type=float, default=0.01, help="Krok czasowy [s]"
    )
    
    args = parser.parse_args()
    compare_aero_configs(args.track, args.dt)


if __name__ == "__main__":
    main()
