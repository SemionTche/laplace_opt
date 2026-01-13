from abc import ABC, abstractmethod

class AcquisitionStructure(ABC):
    display_name: str = "Base acquisition"
    parameters: dict = {}

    @abstractmethod
    def build(self, model, context, **params):
        pass
