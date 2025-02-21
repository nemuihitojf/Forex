from enum import IntEnum
from typing import Any, Optional, SupportsFloat, TypeVar

import numpy as np
import pandas as pd
from pydantic import BaseModel, Field, field_validator

ArrayLike = TypeVar('ArrayLike')

class OrderType(IntEnum):
    BUY: int = 0
    SELL: int = 1

class Order(BaseModel):
    type: OrderType
    volume: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

class ExchangeSettings(BaseModel):
    leverage: int = Field(1, ge=1)
    contract_size: float = Field(100_000.0, gt=0.0)

    spread: float = Field(0.0, ge=0.0)
    commission: float = Field(0.0, ge=0.0)

    one_pip: float = Field(0.0001, gt=0.0)
    swap: bool = Field(False)
    swap_long: Optional[float] = None
    swap_short: Optional[float] = None

    @field_validator('swap')
    @classmethod
    def check_swap(cls, v, values):
        if v:
            if values.get('swap_long') is None or values.get('swap_short') is None:
                raise ValueError("swap_long and swap_short must be provided if swap is True")
        return v

class SimpleExchange:
    def __init__(
        self,
        settings: ExchangeSettings,
        ohlc: pd.DataFrame,
        window_size: int
    ):
        ...

class Exchange:
    def __init__(
        self,
        ohlc: pd.DataFrame,
        window_size: int
    ):
        self.ohlc: pd.DataFrame = ohlc
        self.window_size: int = window_size

        self.index: int = 0
        self._end_index: int = self.ohlc.shape[0] - window_size

        self.orders: pd.DataFrame = pd.DataFrame(
        )
        self.history: pd.DataFrame = pd.DataFrame(
        )
    
    def step(
        self,
    ) -> tuple[ArrayLike, bool, dict[str, Any]]:
        self.index += 1
        terminated: bool = self.index >= self._end_index
        info: dict[str, Any] = {}
        return self.ohlc.iloc[self.index:self.index+self.window_size], terminated, info
    
    def reset(
        self,
        options: Optional[dict[str, float]] = None
    ) -> tuple[ArrayLike, dict[str, Any]]:
        self.index = 0

        info: dict[str, Any] = {}
        return self.ohlc.iloc[self.index:self.index+self.window_size], info

    @property
    def _price(self) -> SupportsFloat:
        return self.ohlc.iloc[self.index+self.window_size-1, 3]

    @property
    def _time(self) -> pd.Timestamp:
        return self.ohlc.index[self.index+self.window_size-1]

    def order_check(
        self,
        order: Order
    ) -> bool:
        price: SupportsFloat = self._price
        if order.type == OrderType.BUY:
            return price < order.stop_loss and price > order.take_profit
        elif order.type == OrderType.SELL:
            return price > order.stop_loss and price < order.take_profit

    def order_send(
        self,
        order: Order
    ) -> None:
        if self.order_check(order):
            order_series: pd.Series = pd.Series(
                {
                    "time": self._time,
                    "type": order.type,
                    "volume": order.volume,
                    "price_open": self._price,
                    "stop_loss": order.stop_loss,
                    "take_profit": order.take_profit
                }
            )
            self.orders = pd.concat([self.orders, order_series], axis=1)
            return None
        raise ValueError("Order is not valid")
