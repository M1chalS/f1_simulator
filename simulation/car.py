from __future__ import annotations

from dataclasses import dataclass

@dataclass
class Car:
    mass: float = 798.0
    engine_force: float = 8000.0
    drag_coefficient: float = 0.9
    lift_coefficient: float = 3.0
    frontal_area: float = 1.5
    tire_friction: float = 1.7
    max_braking_force: float = 40000.0

    def __post_init__(self) -> None:
        if self.mass <= 0:
            raise ValueError("Masa bolidu musi być dodatnia.")
        if self.frontal_area <= 0:
            raise ValueError("Pole powierzchni czołowej musi być dodatnie.")