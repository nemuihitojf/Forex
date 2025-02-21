from typing import Any

import numpy as np
import pandas as pd

class Order:
    ...

class Exchange:
    def __init__(self, ohlc: np.ndarray, window_size: int):
        self.ohlc: np.ndarray = ohlc
        self.window_size: int = window_size

        self.index: int = 0
        self._end_index: int = self.ohlc.shape[0] - window_size

        self.orders: pd.DataFrame = pd.DataFrame(

        )
    
    def step(
        self,
    ) -> tuple[np.ndarray, bool, dict[str, Any]]:
        self.index += 1
        terminated: bool = self.index >= self._end_index
        info: dict[str, Any] = {}
        return self.ohlc[self.index:self.index+self.window_size], terminated, info

    def reset(self) -> tuple[np.ndarray, dict[str, Any]]:
        self.index = 0
        info: dict[str, Any] = {}
        return self.ohlc[self.index:self.index+self.window_size], info