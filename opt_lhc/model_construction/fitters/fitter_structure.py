from abc import ABC, abstractmethod

class FitterStructure(ABC):
    display_name: str = "Base fitter"
    parameters: dict = {}

    @abstractmethod
    def fit(self, model, **params):
        pass
