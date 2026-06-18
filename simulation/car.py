from __future__ import annotations

from dataclasses import dataclass

@dataclass
class Car:
    mass: float = 798.0
    # Moc jednostki napędowej [W]. ~760 kW ≈ 1020 KM (ICE + ERS).
    engine_power: float = 760000.0
    drag_coefficient: float = 0.9
    lift_coefficient: float = 5.8
    frontal_area: float = 1.5
    tire_friction: float = 1.5
    max_braking_force: float = 36000.0
    # Maksymalna prędkość wynikająca z przełożeń skrzyni [m/s]. Około 355 km/h.
    max_speed: float = 98.6
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
            "drag_coefficient": 1.45,
            "lift_coefficient": 7.5,
            "aero_config": "high_downforce"
        }
        defaults.update(kwargs)
        return cls(**defaults)

    # Konfiguracja niskiego oporu = szybsze proste, wolniejsze zakręty.
    @classmethod
    def low_drag(cls, **kwargs) -> "Car":
        defaults = {
            "drag_coefficient": 0.7,
            "lift_coefficient": 5.0,
            "aero_config": "low_drag"
        }
        defaults.update(kwargs)
        return cls(**defaults)

    # Zrównoważona konfiguracja = kompromis między dociskiem a oporem.
    @classmethod
    def balanced(cls, **kwargs) -> "Car":
        defaults = {
            "drag_coefficient": 0.95,
            "lift_coefficient": 5.8,
            "aero_config": "balanced"
        }
        defaults.update(kwargs)
        return cls(**defaults)
