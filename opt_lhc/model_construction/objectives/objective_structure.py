from abc import ABC, abstractmethod

class ObjectiveStructure(ABC):
    
    def __init__(self, name: str, minimize: bool, unit: str):

        self._name = name
        self._minimize = minimize  
        self._unit = unit
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def minimize(self) -> bool:
        return self._minimize
    
    @property
    def unit(self) -> str:
        return self._unit

    @abstractmethod
    def get_value(self) -> None:
        """
        return the current value of the input.
        Must be implemented by subclasses.
        """
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}', minimize='{self.minimize}', unit='{self.unit}')>"