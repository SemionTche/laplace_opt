# libraries
from abc import ABC, abstractmethod

class AcquisitionStructure(ABC):
    display_name: str = "Acquisition Structure"
    parameters: dict = {}

    @abstractmethod
    def build(self, model, context, **params):
        pass
