from abc import ABC, abstractmethod

class ObjectiveStructure(ABC):
    
    def __init__(self, name: str, unit: str, default_minimize: bool):

        self._name = name
        self._unit = unit
        self.default_minimize = default_minimize
        self._minimize = default_minimize
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def minimize(self) -> bool:
        return self._minimize
    
    @property
    def unit(self) -> str:
        return self._unit
    
    def set_minimize(self, minimize: bool) -> None:
        self._minimize = minimize

    @abstractmethod
    def get_value(self) -> None:
        """
        return the current value of the input.
        Must be implemented by subclasses.
        """
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}', minimize='{self.minimize}', unit='{self.unit}')>"