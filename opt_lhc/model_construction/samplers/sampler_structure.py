from abc import ABC, abstractmethod

class SamplerStructure(ABC):
    display_name: str = "Base sampler"
    parameters: dict = {}

    @abstractmethod
    def build(self, **params):
        pass
