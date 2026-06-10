from __future__ import annotations

import math

# Gęstość powietrza na poziomie morza [kg/m^3]
AIR_DENSITY = 1.225

# Przyspieszenie ziemskie [m/s^2]
GRAVITY = 9.81

# Oblicza siłę oporu aerodynamicznego -> F_drag = .5 * rho * Cd * A * v^2
def drag_force(velocity: float, drag_coefficient: float,
               frontal_area: float, air_density: float = AIR_DENSITY) -> float:
    return 0.5 * air_density * drag_coefficient * frontal_area * velocity ** 2

# Oblicza siłę docisku aerodynamicznego -> F_downforce = .5 * rho * CL * A * v^2
def downforce(velocity: float, lift_coefficient: float,
              frontal_area: float, air_density: float = AIR_DENSITY) -> float:
    return 0.5 * air_density * lift_coefficient * frontal_area * velocity ** 2

# Zwraca siłę napędową silnika
# TODO Dokończyć
def engine_force(max_engine_force: float) -> float:
    return max_engine_force

# Oblicza maksymalną bezpieczną prędkość w zakręcie.
def max_corner_velocity(radius: float, tire_friction: float, mass: float,
                        lift_coefficient: float, frontal_area: float,
                        air_density: float = AIR_DENSITY,
                        gravity: float = GRAVITY) -> float:
    # Współczynnik dla docisku
    k = radius * tire_friction * 0.5 * air_density * lift_coefficient * frontal_area / mass

    # Zabezpieczenie przed dzieleniem przez zero lub wartościami ujemnymi
    if k >= 1.0:
        # Przy bardzo silnym docisku teoretycznie prędkość mogłaby być nieograniczona
        return 150.0  # ~540 km/h - górne ograniczenie

    denominator = 1.0 - k
    if denominator <= 0:
        return 150.0

    v_max_squared = radius * tire_friction * gravity / denominator

    if v_max_squared < 0:
        return 0.0

    return math.sqrt(v_max_squared)

# Oblicza drogę hamowania od prędkości początkowej do końcowej.
def braking_distance(initial_velocity: float, final_velocity: float,
                    max_braking_force: float, mass: float,
                    drag_coefficient: float, frontal_area: float,
                    air_density: float = AIR_DENSITY) -> float:
    if initial_velocity <= final_velocity:
        return 0.0

    avg_velocity = (initial_velocity + final_velocity) / 2.0
    avg_drag = drag_force(avg_velocity, drag_coefficient, frontal_area, air_density)

    total_braking = max_braking_force + avg_drag
    deceleration = total_braking / mass

    distance = (final_velocity**2 - initial_velocity**2) / (-2 * deceleration)

    return max(0.0, distance)


