from abc import ABC, abstractmethod
from typing import Sequence

def check_bounds_format(bounds: Sequence[float]):
    """
    checks if the boundaries provided respect the format:
        length = 2 and minimum in first position.
    """
    if len(bounds) != 2 or bounds[0] > bounds[1]:
        raise ValueError("bounds must have exactly 2 elements: (min, max)")

class InputStructure(ABC):
    
    def __init__(self, name: str, bounds: Sequence[float], safe_bounds: Sequence[float], unit: str, address: str):
        check_bounds_format(bounds)
        check_bounds_format(safe_bounds)

        self._name = name
        self._address = address
        self._bounds = bounds
        self._safe_bounds = safe_bounds
        self._unit = unit
    
    @property
    def name(self) -> str:
        return self._name

    @property
    def bounds(self) -> Sequence[float]:
        return self._bounds

    @property
    def safe_bounds(self) -> Sequence[float]:
        return self._safe_bounds    
    
    @property
    def address(self) -> str:
        return self._address
    
    @property
    def unit(self) -> str:
        return self._unit

    @abstractmethod
    def get_position(self) -> None:
        """
        return the current position of the input.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def set_position(self, position: float) -> None:
        """
        set the position of the input.
        Must be implemented by subclasses.
        """
        pass

    def set_bounds(self, new_bounds: Sequence[float]) -> None:
        check_bounds_format(new_bounds)
        self._bounds = new_bounds

    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}', bounds={self.bounds}, unit='{self.unit}', safe_bounds={self.safe_bounds}, address={self.address})>"