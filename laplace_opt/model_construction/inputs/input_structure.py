# libraries
from abc import ABC
from typing import Sequence


def check_bounds_format(bounds: Sequence[float]):
    '''
    checks if the boundaries provided respect the format:
        length = 2 and minimum in first position.
    '''
    if len(bounds) != 2 or bounds[0] > bounds[1]:
        raise ValueError("bounds must have exactly 2 elements: (min, max)")


class InputStructure(ABC):
    '''
    Abstract base class describing an optimization input variable.

    Stores bounds, hardware address, metadata, and position index
    used to map values inside payloads.
    '''
    
    def __init__(self, 
                 name: str,
                 bounds: Sequence[float], 
                 safe_bounds: Sequence[float], 
                 unit: str,
                 ip: str,
                 port: str, 
                 description: str,
                 symbol: str,
                 position_index: int):
        '''
        Initialize an input definition.

            Args:
                name: (str) 
                    Variable name.
                
                bounds: (Sequence[float])
                    Optimization bounds (min, max).
                
                safe_bounds: (Sequence[float]) 
                    Hardware-safe bounds (min, max).
                
                unit: (str) 
                    Physical unit.
                
                ip: (str)
                    Device IP address.
                
                port: (str)
                    Device port.
                
                description: (str) 
                    Human-readable description.
                
                symbol: (str) 
                    Short symbol for display.
                
                position_index: (int) 
                    Index in payload vector.
        '''
        
        check_bounds_format(bounds)
        check_bounds_format(safe_bounds)

        self.name = name
        self.ip = ip
        self.port = port
        self._bounds = bounds
        self._safe_bounds = safe_bounds
        self._unit = unit

        self.position_index = position_index

        self.description = description
        self.symbol = symbol

    @property
    def bounds(self) -> Sequence[float]:
        return self._bounds

    @property
    def safe_bounds(self) -> Sequence[float]:
        return self._safe_bounds    
    
    @property
    def address(self) -> str:
        return self.ip_port
    
    @property
    def ip_port(self) -> str:
        return f"{self.ip}:{self.port}"
    
    @property
    def unit(self) -> str:
        return self._unit


    def set_bounds(self, new_bounds: Sequence[float]) -> None:
        check_bounds_format(new_bounds)
        self._bounds = new_bounds


    def __repr__(self):
        '''Compact representation.'''
        return (
            f"<{self.__class__.__name__}("
            f"name='{self.name}', "
            f"bounds={self.bounds}, "
            f"unit='{self.unit}', "
            f"safe_bounds={self.safe_bounds}, "
            f"address={self.address}), "
            f"position index={self.position_index}>"
        )