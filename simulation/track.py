from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Segment:
    type: str
    length: float | None = None
    radius: float | None = None
    angle: float | None = None

    def __post_init__(self) -> None:
        if self.type == "straight":
            if self.length is None or self.length <= 0:
                raise ValueError("Prosta wymaga dodatniej długości 'length'.")
        elif self.type == "corner":
            if self.radius is None or self.radius <= 0:
                raise ValueError("Zakręt wymaga dodatniego promienia 'radius'.")
            if self.angle is None or self.angle <= 0:
                raise ValueError("Zakręt wymaga dodatniego kąta 'angle'.")
        else:
            raise ValueError(f"Nieznany typ segmentu: {self.type!r}")

    # Długość łuku zakrętu [m] = r * kąt_w_radianach.
    def arc_length(self) -> float:
        if self.type != "corner" or self.radius is None or self.angle is None:
            raise AttributeError("arc_length dotyczy tylko zakrętów.")
        import math
        return self.radius * math.radians(self.angle)

    # Długość segmentu wzdłuż toru [m] niezależnie od jego typu.
    def segment_length(self) -> float:
        if self.type == "straight" and self.length is not None:
            return float(self.length)
        return self.arc_length()


class Track:
    def __init__(self, segments: list[Segment], name: str = "Unnamed") -> None:
        if not segments:
            raise ValueError("Tor musi zawierać co najmniej jeden segment.")
        self.segments = segments
        self.name = name

    @property
    def total_length(self) -> float:
        return sum(seg.segment_length() for seg in self.segments)

    def __iter__(self):
        return iter(self.segments)

    def __len__(self) -> int:
        return len(self.segments)

    @classmethod
    def from_list(cls, data: list[dict], name: str = "Unnamed") -> "Track":
        segments = [Segment(**item) for item in data]
        return cls(segments, name=name)

    # Wczytuje tor z pliku JSON: {"name": ..., "segments": [...]}
    @classmethod
    def from_json(cls, path: str | Path, name: str | None = None) -> "Track":
        path = Path(path)
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)

        if isinstance(data, dict):
            segments_data = data.get("segments", [])
            track_name = name or data.get("name", path.stem)
        else:
            segments_data = data
            track_name = name or path.stem

        return cls.from_list(segments_data, name=track_name)


