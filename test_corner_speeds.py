from physics import forces
from simulation.car import Car
from simulation.track import Track

def main():
    car = Car()
    track = Track.from_json("data/tracks.json")

    print("=" * 60)
    print("ANALIZA MAKSYMALNYCH PRĘDKOŚCI W ZAKRĘTACH")
    print("=" * 60)
    print(f"\nParametry bolidu:")
    print(f"  Masa: {car.mass} kg")
    print(f"  Współczynnik przyczepności: {car.tire_friction}")
    print(f"  Współczynnik docisku (CL): {car.lift_coefficient}")
    print(f"  Pole czołowe: {car.frontal_area} m²")
    print()

    for i, segment in enumerate(track.segments):
        if segment.type == "corner":
            max_v = forces.max_corner_velocity(
                radius=segment.radius or 0.0,
                tire_friction=car.tire_friction,
                mass=car.mass,
                lift_coefficient=car.lift_coefficient,
                frontal_area=car.frontal_area
            )

            arc_length = segment.arc_length()

            print(f"Segment {i} - Zakręt:")
            print(f"  Promień: {segment.radius} m")
            print(f"  Kąt: {segment.angle}°")
            print(f"  Długość łuku: {arc_length:.1f} m")
            print(f"  Maksymalna prędkość: {max_v:.1f} m/s ({max_v * 3.6:.1f} km/h)")

            downforce_at_max = forces.downforce(
                max_v, car.lift_coefficient, car.frontal_area
            )
            print(f"  Docisk przy V_max: {downforce_at_max:.0f} N ({downforce_at_max/9.81:.0f} kg)")

            centripetal_force = car.mass * max_v**2 / (segment.radius or 1.0)
            print(f"  Siła dośrodkowa: {centripetal_force:.0f} N")
            print()

if __name__ == "__main__":
    main()

