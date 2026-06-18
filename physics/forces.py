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

# Zwraca siłę napędową dostępną przy danej prędkości.
def engine_force(velocity: float, max_power: float,
                 traction_limit: float) -> float:
    v = max(velocity, 1.0)
    power_limited = max_power / v
    return min(power_limited, traction_limit)

# Maksymalna siła wzdłużna, jaką opony mogą przekazać na asfalt.
def traction_limit(velocity: float, tire_friction: float, mass: float,
                   lift_coefficient: float, frontal_area: float,
                   air_density: float = AIR_DENSITY,
                   gravity: float = GRAVITY) -> float:
    f_down = downforce(velocity, lift_coefficient, frontal_area, air_density)
    normal_force = mass * gravity + f_down
    return tire_friction * normal_force

# Maksymalne boczne przyspieszenie, jakie opony F1 są w stanie utrzymać [g].
MAX_LATERAL_G = 5.5

# Oblicza maksymalną bezpieczną prędkość w zakręcie.
def max_corner_velocity(radius: float, tire_friction: float, mass: float,
                        lift_coefficient: float, frontal_area: float,
                        air_density: float = AIR_DENSITY,
                        gravity: float = GRAVITY,
                        max_lateral_g: float = MAX_LATERAL_G) -> float:
    # Limit saturacji opon: niezależnie od docisku opona nie przekroczy pewnego
    v_sat = math.sqrt(max_lateral_g * gravity * radius)

    # Limit z bilansu przyczepności (model punktowy z dociskiem):
    k = radius * tire_friction * 0.5 * air_density * lift_coefficient * frontal_area / mass

    # Zabezpieczenie przed dzieleniem przez zero lub wartościami ujemnymi
    if k >= 1.0:
        return v_sat

    v_grip = math.sqrt(radius * tire_friction * gravity / (1.0 - k))

    # Rzeczywista prędkość = mniejszy z dwóch limitów.
    return min(v_grip, v_sat)

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

# Dokładniejsze obliczanie drogi hamowania metodą numeryczną
def braking_distance_precise(initial_velocity: float, final_velocity: float,
                             max_braking_force: float, mass: float,
                             drag_coefficient: float, frontal_area: float,
                             air_density: float = AIR_DENSITY,
                             dt: float = 0.01) -> tuple[float, float]:
    if initial_velocity <= final_velocity:
        return (0.0, 0.0)
    
    v = initial_velocity
    distance = 0.0
    time = 0.0
    
    while v > final_velocity:
        # Oblicz siłę oporu przy aktualnej prędkości
        f_drag = drag_force(v, drag_coefficient, frontal_area, air_density)
        
        # Całkowita siła hamująca
        total_braking = max_braking_force + f_drag
        
        # Opóźnienie
        deceleration = total_braking / mass
        
        # Nowa prędkość
        v_new = v - deceleration * dt
        
        # Jeśli spadliśmy poniżej prędkości docelowej, skoryguj ostatni krok
        if v_new < final_velocity:
            # Oblicz dokładnie potrzebny czas do osiągnięcia v_final
            dt_actual = (v - final_velocity) / deceleration
            distance += v * dt_actual - 0.5 * deceleration * dt_actual ** 2
            time += dt_actual
            break
        
        # Standardowy krok
        distance += v * dt - 0.5 * deceleration * dt ** 2
        time += dt
        v = v_new
    
    return (max(0.0, distance), time)

# Oblicza energię rozpraszaną podczas hamowania
def braking_energy(initial_velocity: float, final_velocity: float,
                   mass: float) -> float:
    return 0.5 * mass * (initial_velocity**2 - final_velocity**2)


