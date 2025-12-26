from abc import ABC, abstractmethod

class ModelStructure(ABC):
    display_name: str = "Base model"
    parameters: dict = {}

    @abstractmethod
    def build(self, train_X, train_Y, **params):
        pass
