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
    drag_force: list[float] = field(default_factory=list)
    downforce: list[float] = field(default_factory=list)
    state: list[str] = field(default_factory=list)  # "accelerating", "braking", "coasting", "cornering"
    braking_points: list[tuple[float, float, float]] = field(default_factory=list)  # (position, velocity, target_velocity)

    def record(self, t: float, x: float, v: float, a: float, seg: int,
               drag: float = 0.0, down: float = 0.0, state: str = "coasting") -> None:
        self.time.append(t)
        self.position.append(x)
        self.velocity.append(v)
        self.acceleration.append(a)
        self.segment_index.append(seg)
        self.drag_force.append(drag)
        self.downforce.append(down)
        self.state.append(state)

    def record_braking_point(self, position: float, velocity: float, target_velocity: float) -> None:
        self.braking_points.append((position, velocity, target_velocity))


@dataclass
class SimulationResult:
    telemetry: Telemetry
    lap_time: float
    max_velocity: float
    avg_velocity: float
    total_distance: float
    max_drag: float = 0.0
    max_downforce: float = 0.0
    avg_drag: float = 0.0
    avg_downforce: float = 0.0
    braking_count: int = 0
    total_braking_distance: float = 0.0
    total_braking_time: float = 0.0

    def summary(self) -> str:
        return (
            f"Czas przejazdu:      {self.lap_time:.2f} s\n"
            f"Dystans:             {self.total_distance:.1f} m\n"
            f"Prędkość maksymalna: {self.max_velocity * 3.6:.1f} km/h "
            f"({self.max_velocity:.1f} m/s)\n"
            f"Prędkość średnia:    {self.avg_velocity * 3.6:.1f} km/h "
            f"({self.avg_velocity:.1f} m/s)\n"
            f"\nAerodynamika:\n"
            f"Max drag:            {self.max_drag:.0f} N\n"
            f"Max downforce:       {self.max_downforce:.0f} N\n"
            f"Avg drag:            {self.avg_drag:.0f} N\n"
            f"Avg downforce:       {self.avg_downforce:.0f} N\n"
            f"\nHamowanie:\n"
            f"Liczba hamowań:      {self.braking_count}\n"
            f"Całkowity dystans:   {self.total_braking_distance:.1f} m\n"
            f"Całkowity czas:      {self.total_braking_time:.2f} s"
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
        target_velocity = corner_info[1] if corner_info is not None else None

        # Symulacja prostej
        vehicle_state = "accelerating"
        while state["position"] < segment_end:
            v = state["velocity"]

            # Oblicz siły aerodynamiczne
            f_drag = forces.drag_force(
                v, self.car.drag_coefficient, self.car.frontal_area
            )
            f_downforce = forces.downforce(
                v, self.car.lift_coefficient, self.car.frontal_area
            )

            # Czy MUSIMY już hamować? Decyzję podejmujemy DYNAMICZNIE co krok na
            # podstawie AKTUALNEJ prędkości i pozostałego dystansu do zakrętu
            need_brake = False
            if corner_info is not None and v > target_velocity:
                distance_to_corner, max_corner_v = corner_info
                remaining = (segment_end - state["position"]) + distance_to_corner
                brake_dist = forces.braking_distance(
                    initial_velocity=v,
                    final_velocity=max_corner_v,
                    max_braking_force=self.car.max_braking_force,
                    mass=self.car.mass,
                    drag_coefficient=self.car.drag_coefficient,
                    frontal_area=self.car.frontal_area
                )
                # Margines bezpieczeństwa 2% — zaczynamy hamować nieco wcześniej.
                if remaining <= brake_dist * 1.02:
                    need_brake = True

            if need_brake:
                # Rejestruj punkt hamowania (tylko raz, przy wejściu w hamowanie)
                if vehicle_state != "braking":
                    telemetry.record_braking_point(state["position"], v, target_velocity or 0.0)

                # Hamowanie
                net_force = -(self.car.max_braking_force + f_drag)
                a = dynamics.acceleration(net_force, self.car.mass)
                vehicle_state = "braking"

                # Nie hamuj poniżej prędkości docelowej
                if target_velocity is not None and v <= target_velocity:
                    a = 0.0
                    vehicle_state = "coasting"
            else:
                # Przyspieszanie — siła ograniczona mocą silnika ORAZ przyczepnością
                # (przyczepność rośnie z dociskiem, więc docisk pomaga na wyjściu z zakrętu)
                f_traction = forces.traction_limit(
                    v, self.car.tire_friction, self.car.mass,
                    self.car.lift_coefficient, self.car.frontal_area
                )
                f_engine = forces.engine_force(
                    v, self.car.engine_power, f_traction
                )
                net_force = f_engine - f_drag
                a = dynamics.acceleration(net_force, self.car.mass)
                vehicle_state = "accelerating"

            new_x, new_v = dynamics.integrate_step(
                state["position"], v, a, self.dt
            )
            # Ogranicznik prędkości (przełożenia skrzyni biegów).
            if new_v > self.car.max_speed:
                new_v = self.car.max_speed
            state["position"] = new_x
            state["velocity"] = new_v
            state["time"] += self.dt

            telemetry.record(
                state["time"], state["position"], state["velocity"], a, seg_index,
                drag=f_drag, down=f_downforce, state=vehicle_state
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

            # Oblicz siły aerodynamiczne
            f_drag = forces.drag_force(
                v, self.car.drag_coefficient, self.car.frontal_area
            )
            f_downforce = forces.downforce(
                v, self.car.lift_coefficient, self.car.frontal_area
            )

            # Jeśli jedziemy wolniej niż max, próbujemy przyspieszyć na wyjściu
            if v < max_v * 0.95:  # 5% margines
                # Koło tarcia: w zakręcie część przyczepności zużywa siła dośrodkowa
                f_traction = forces.traction_limit(
                    v, self.car.tire_friction, self.car.mass,
                    self.car.lift_coefficient, self.car.frontal_area
                ) * 0.7
                f_engine = forces.engine_force(
                    v, self.car.engine_power, f_traction
                )
                net_force = f_engine - f_drag
                a = dynamics.acceleration(net_force, self.car.mass)
                vehicle_state = "cornering_accel"
            elif v > max_v:
                # Za szybko - pełne hamowanie
                net_force = -(self.car.max_braking_force + f_drag)
                a = dynamics.acceleration(net_force, self.car.mass)
                vehicle_state = "cornering_brake"
            else:
                # Idealna prędkość - utrzymywanie
                a = dynamics.acceleration(-f_drag, self.car.mass)
                vehicle_state = "cornering"

            new_x, new_v = dynamics.integrate_step(
                state["position"], v, a, self.dt
            )
            # Twarde egzekwowanie granicy przyczepności: w zakręcie bolid nie może
            # przekroczyć prędkości maksymalnej (inaczej fizycznie wypadłby z toru).
            if new_v > max_v:
                new_v = max_v
            state["position"] = new_x
            state["velocity"] = new_v
            state["time"] += self.dt

            telemetry.record(
                state["time"], state["position"], state["velocity"], a, seg_index,
                drag=f_drag, down=f_downforce, state=vehicle_state
            )

    def run(self) -> SimulationResult:
        telemetry = Telemetry()
        state = {"position": 0.0, "velocity": 0.0, "time": 0.0}

        telemetry.record(0.0, 0.0, 0.0, 0.0, 0, drag=0.0, down=0.0, state="start")

        for i, segment in enumerate(self.track):
            if segment.type == "straight":
                self._simulate_straight(segment, telemetry, i, state)
            elif segment.type == "corner":
                self._simulate_corner(segment, telemetry, i, state)

        velocities = telemetry.velocity
        max_v = max(velocities) if velocities else 0.0
        avg_v = (state["position"] / state["time"]) if state["time"] > 0 else 0.0
        
        # Statystyki aerodynamiczne
        max_drag = max(telemetry.drag_force) if telemetry.drag_force else 0.0
        max_down = max(telemetry.downforce) if telemetry.downforce else 0.0
        avg_drag = sum(telemetry.drag_force) / len(telemetry.drag_force) if telemetry.drag_force else 0.0
        avg_down = sum(telemetry.downforce) / len(telemetry.downforce) if telemetry.downforce else 0.0
        
        # Statystyki hamowania
        braking_count = len(telemetry.braking_points)
        total_braking_distance = 0.0
        total_braking_time = 0.0
        
        # Oblicz całkowity dystans i czas hamowania
        in_braking = False
        braking_start_idx = 0
        
        for i, state_name in enumerate(telemetry.state):
            if state_name == "braking" and not in_braking:
                in_braking = True
                braking_start_idx = i
            elif state_name != "braking" and in_braking:
                in_braking = False
                # Oblicz dystans i czas hamowania
                if i > braking_start_idx:
                    brake_dist = telemetry.position[i] - telemetry.position[braking_start_idx]
                    brake_time = telemetry.time[i] - telemetry.time[braking_start_idx]
                    total_braking_distance += brake_dist
                    total_braking_time += brake_time

        return SimulationResult(
            telemetry=telemetry,
            lap_time=state["time"],
            max_velocity=max_v,
            avg_velocity=avg_v,
            total_distance=state["position"],
            max_drag=max_drag,
            max_downforce=max_down,
            avg_drag=avg_drag,
            avg_downforce=avg_down,
            braking_count=braking_count,
            total_braking_distance=total_braking_distance,
            total_braking_time=total_braking_time,
        )

