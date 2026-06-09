from __future__ import annotations

# Gęstość powietrza na poziomie morza [kg/m^3]
AIR_DENSITY = 1.225

# Przyspieszenie ziemskie [m/s^2]
GRAVITY = 9.81

# Oblicza siłę oporu aerodynamicznego -> F_drag = .5 * rho * Cd * A * v^2
def drag_force(velocity: float, drag_coefficient: float,
               frontal_area: float, air_density: float = AIR_DENSITY) -> float:
    return .5 * air_density * drag_coefficient * frontal_area * velocity ** 2

# Zwraca siłę napędową silnika
# TODO Dokończyć
def engine_force(max_engine_force: float) -> float:
    return max_engine_force

