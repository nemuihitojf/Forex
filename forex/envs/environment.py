from typing import Any, SupportsFloat

import gymnasium
from gymnasium import spaces
from gymnasium.core import ActType, ObsType, RenderFrame
import numpy as np
import pandas as pd

class Environment(gymnasium.Env):
    metadata: dict[str, Any] = {
        "render_modes": []
    }

    def __init__(
        self,
        history: np.ndarray,
        window_size: int
    ):
        super(Environment, self).__init__()
        # length * num_features
        self.history: np.ndarray = history
        self.window_size: int = window_size
        
        self.observation_space = spaces.Box(
            low=-float("inf"),
            high=float("inf"),
            shape=(self.history.shape[1], window_size, ),
            dtype=np.float32
        )

        self.index: int = 0
        self._end_index: int = self.history.shape[0] - window_size

    def step(
        self,
        action: ActType
    ) -> tuple[ObsType, SupportsFloat, bool, bool, dict[str, Any]]:
        ...

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, Any] | None = None
    ) -> tuple[ObsType, dict[str, Any]]:
        super(Environment, self).reset(seed=seed)
        self.index = 0
    
    def render(self) -> RenderFrame | list[RenderFrame] | None:
        ...
    
    def close(self) -> None:
        ...

class ForexEnv(Environment):
    action_space = spaces.Discrete(3)