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

    def _simulate_straight(self, segment: Segment, telemetry: Telemetry,
                           seg_index: int, state: dict) -> None:
        target_distance = state["position"] + segment.segment_length()

        while state["position"] < target_distance:
            v = state["velocity"]

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

    def run(self) -> SimulationResult:
        telemetry = Telemetry()
        state = {"position": 0.0, "velocity": 0.0, "time": 0.0}

        telemetry.record(0.0, 0.0, 0.0, 0.0, 0)

        for i, segment in enumerate(self.track):
            if segment.type == "straight":
                self._simulate_straight(segment, telemetry, i, state)
            elif segment.type == "corner":
                # TODO: Pełna fizyka (siła dośrodkowa, przyczepność)
                v = max(state["velocity"], 1e-6)
                corner_time = segment.segment_length() / v
                steps = max(1, int(corner_time / self.dt))
                for _ in range(steps):
                    new_x, new_v = dynamics.integrate_step(
                        state["position"], state["velocity"], 0.0, self.dt
                    )
                    state["position"] = new_x
                    state["velocity"] = new_v
                    state["time"] += self.dt
                    telemetry.record(
                        state["time"], state["position"],
                        state["velocity"], 0.0, i
                    )

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

