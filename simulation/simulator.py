from __future__ import annotations

from dataclasses import dataclass, field

from physics import dynamics, forces
from simulation.car import Car
from simulation.track import Segment, Track

@dataclass
class Telemetry:
    time: list[float] = field(default_factory=list)
    position: list[float] = field(default_factory=list)
    velocity: list[float] = field(default_factory=list)
    acceleration: list[float] = field(default_factory=list)
    segment_index: list[int] = field(default_factory=list)

    def record(self, t: float, x: float, v: float, a: float, seg: int) -> None:
        self.time.append(t)
        self.position.append(x)
        self.velocity.append(v)
        self.acceleration.append(a)
        self.segment_index.append(seg)


@dataclass
class SimulationResult:
    telemetry: Telemetry
    lap_time: float
    max_velocity: float
    avg_velocity: float
    total_distance: float

    def summary(self) -> str:
        return (
            f"Czas przejazdu:      {self.lap_time:.2f} s\n"
            f"Dystans:             {self.total_distance:.1f} m\n"
            f"Prędkość maksymalna: {self.max_velocity * 3.6:.1f} km/h "
            f"({self.max_velocity:.1f} m/s)\n"
            f"Prędkość średnia:    {self.avg_velocity * 3.6:.1f} km/h "
            f"({self.avg_velocity:.1f} m/s)"
        )


class Simulator:
    def __init__(self, car: Car, track: Track, dt: float = 0.01) -> None:
        if dt <= 0:
            raise ValueError("Krok czasowy dt musi być dodatni.")
        self.car = car
        self.track = track
        self.dt = dt

    # Czy następny segment to zakręt i max speed
    def _get_next_corner_info(self, current_index: int) -> tuple[float, float] | None:
        distance_to_corner = 0.0

        for i in range(current_index + 1, len(self.track.segments)):
            segment = self.track.segments[i]

            if segment.type == "corner":
                max_v = forces.max_corner_velocity(
                    radius=segment.radius or 0.0,
                    tire_friction=self.car.tire_friction,
                    mass=self.car.mass,
                    lift_coefficient=self.car.lift_coefficient,
                    frontal_area=self.car.frontal_area
                )
                return (distance_to_corner, max_v)
            else:
                distance_to_corner += segment.segment_length()

        return None

    def _simulate_straight(self, segment: Segment, telemetry: Telemetry,
                           seg_index: int, state: dict) -> None:
        segment_start = state["position"]
        segment_end = segment_start + segment.segment_length()

        corner_info = self._get_next_corner_info(seg_index)

        braking_point = None
        target_velocity = None

        if corner_info is not None:
            distance_to_corner, max_corner_v = corner_info
            current_v = state["velocity"]

            if current_v > max_corner_v:
                brake_dist = forces.braking_distance(
                    initial_velocity=current_v,
                    final_velocity=max_corner_v,
                    max_braking_force=self.car.max_braking_force,
                    mass=self.car.mass,
                    drag_coefficient=self.car.drag_coefficient,
                    frontal_area=self.car.frontal_area
                )

                # Punkt hamowania = koniec prostej - dystans do zakrętu + margines bezpieczeństwa (95% drogi hamowania)
                braking_point = segment_end + distance_to_corner - brake_dist * 1.05
                target_velocity = max_corner_v

        # Symulacja prostej
        while state["position"] < segment_end:
            v = state["velocity"]

            # Sprawdź czy jesteśmy w fazie hamowania
            if braking_point is not None and state["position"] >= braking_point:
                # Hamowanie
                f_drag = forces.drag_force(
                    v, self.car.drag_coefficient, self.car.frontal_area
                )
                net_force = -(self.car.max_braking_force + f_drag)
                a = dynamics.acceleration(net_force, self.car.mass)

                # Nie hamuj poniżej prędkości docelowej
                if target_velocity is not None and v <= target_velocity:
                    a = 0.0
            else:
                # Przyspieszanie
                f_engine = forces.engine_force(self.car.engine_force)
                f_drag = forces.drag_force(
                    v, self.car.drag_coefficient, self.car.frontal_area
                )
                net_force = f_engine - f_drag
                a = dynamics.acceleration(net_force, self.car.mass)

            new_x, new_v = dynamics.integrate_step(
                state["position"], v, a, self.dt
            )
            state["position"] = new_x
            state["velocity"] = new_v
            state["time"] += self.dt

            telemetry.record(
                state["time"], state["position"], state["velocity"], a, seg_index
            )

    # Symulacja zakrętu - utrzymywanie prędkości bliskiej maksymalnej bezpiecznej
    def _simulate_corner(self, segment: Segment, telemetry: Telemetry,
                        seg_index: int, state: dict) -> None:
        if segment.radius is None:
            raise ValueError("Zakręt musi mieć zdefiniowany promień.")

        # Oblicz maksymalną bezpieczną prędkość w tym zakręcie
        max_v = forces.max_corner_velocity(
            radius=segment.radius,
            tire_friction=self.car.tire_friction,
            mass=self.car.mass,
            lift_coefficient=self.car.lift_coefficient,
            frontal_area=self.car.frontal_area
        )

        segment_start = state["position"]
        segment_end = segment_start + segment.segment_length()

        while state["position"] < segment_end:
            v = state["velocity"]

            # Jeśli jedziemy wolniej niż max, próbujemy delikatnie przyspieszyć
            if v < max_v * 0.95:  # 5% margines
                # Delikatne przyspieszanie w zakręcie (ograniczona moc)
                f_engine = forces.engine_force(self.car.engine_force) * 0.3
                f_drag = forces.drag_force(
                    v, self.car.drag_coefficient, self.car.frontal_area
                )
                # Siła dośrodkowa nie wpływa na ruch wzdłuż toru (tylko poprzecznie)
                net_force = f_engine - f_drag
                a = dynamics.acceleration(net_force, self.car.mass)
            elif v > max_v:
                # Za szybko - lekkie hamowanie
                f_drag = forces.drag_force(
                    v, self.car.drag_coefficient, self.car.frontal_area
                )
                braking_force = self.car.max_braking_force * 0.2  # Delikatne hamowanie
                net_force = -(braking_force + f_drag)
                a = dynamics.acceleration(net_force, self.car.mass)
            else:
                # Idealna prędkość - utrzymywanie
                f_drag = forces.drag_force(
                    v, self.car.drag_coefficient, self.car.frontal_area
                )
                a = dynamics.acceleration(-f_drag, self.car.mass)

            new_x, new_v = dynamics.integrate_step(
                state["position"], v, a, self.dt
            )
            state["position"] = new_x
            state["velocity"] = new_v
            state["time"] += self.dt

            telemetry.record(
                state["time"], state["position"], state["velocity"], a, seg_index
            )

    def run(self) -> SimulationResult:
        telemetry = Telemetry()
        state = {"position": 0.0, "velocity": 0.0, "time": 0.0}

        telemetry.record(0.0, 0.0, 0.0, 0.0, 0)

        for i, segment in enumerate(self.track):
            if segment.type == "straight":
                self._simulate_straight(segment, telemetry, i, state)
            elif segment.type == "corner":
                self._simulate_corner(segment, telemetry, i, state)

        velocities = telemetry.velocity
        max_v = max(velocities) if velocities else 0.0
        avg_v = (state["position"] / state["time"]) if state["time"] > 0 else 0.0

        return SimulationResult(
            telemetry=telemetry,
            lap_time=state["time"],
            max_velocity=max_v,
            avg_velocity=avg_v,
            total_distance=state["position"],
        )

