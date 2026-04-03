from __future__ import annotations

from dataclasses import dataclass, field
import random
from typing import Any


@dataclass
class SimulationState:
    """Container for simulation runtime state."""

    lights: Any
    roads: Any
    vehicles: Any
    sim_time: float = 0.0
    rng_seed: int = 42
    rng: random.Random = field(init=False)

    def __post_init__(self) -> None:
        self.rng = random.Random(self.rng_seed)

    def tick(self, dt_seconds: float) -> None:
        if dt_seconds < 0:
            raise ValueError("dt_seconds must be non-negative")
        self.sim_time += dt_seconds
