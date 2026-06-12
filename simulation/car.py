from __future__ import annotations

from dataclasses import dataclass

@dataclass
class Car:
    mass: float = 798.0
    engine_force: float = 8000.0
    drag_coefficient: float = 0.9
    lift_coefficient: float = 6.0
    frontal_area: float = 1.5
    tire_friction: float = 1.6
    max_braking_force: float = 40000.0
    aero_config: str = "balanced"  # "balanced", "high_downforce", "low_drag"

    def __post_init__(self) -> None:
        if self.mass <= 0:
            raise ValueError("Masa bolidu musi być dodatnia.")
        if self.frontal_area <= 0:
            raise ValueError("Pole powierzchni czołowej musi być dodatnie.")

    # Więcej docisku = szybsze zakręty, wolniejsze proste.
    @classmethod
    def high_downforce(cls, **kwargs) -> "Car":
        defaults = {
            "drag_coefficient": 1.0,  # Zmniejszono z 1.05
            "lift_coefficient": 6.8,   # Zwiększono z 3.8
            "aero_config": "high_downforce"
        }
        defaults.update(kwargs)
        return cls(**defaults)

    # Konfiguracja niskiego oporu = szybsze proste, wolniejsze zakręty.
    @classmethod
    def low_drag(cls, **kwargs) -> "Car":
        defaults = {
            "drag_coefficient": 0.7,
            "lift_coefficient": 4.5,
            "aero_config": "low_drag"
        }
        defaults.update(kwargs)
        return cls(**defaults)

    # Zrównoważona konfiguracja = kompromis między dociskiem a oporem.
    @classmethod
    def balanced(cls, **kwargs) -> "Car":
        defaults = {
            "drag_coefficient": 0.9,
            "lift_coefficient": 5.8,
            "aero_config": "balanced"
        }
        defaults.update(kwargs)
        return cls(**defaults)
