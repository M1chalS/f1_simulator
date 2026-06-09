from __future__ import annotations

# Przyspieszenie z II zasady Newtona
def acceleration(net_force: float, mass: float) -> float:
    if mass <= 0:
        raise ValueError("Masa musi być dodatnia.")
    return net_force / mass

# Wykonuje jeden krok całkowania metodą Eulera
def integrate_step(position: float, velocity: float, accel: float,
                   dt: float) -> tuple[float, float]:
    new_velocity = velocity + accel * dt
    if new_velocity < 0:
        new_velocity = 0.0
    new_position = position + velocity * dt
    return new_position, new_velocity

