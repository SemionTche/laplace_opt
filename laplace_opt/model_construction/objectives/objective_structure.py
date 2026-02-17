# libraries
from abc import ABC


class ObjectiveStructure(ABC):
    '''
    Base abstract structure describing an optimization objective.

    This class stores all metadata required to:
    - identify the objective,
    - connect to its data source,
    - define its optimization direction,
    - map the received measurement to a specific output key.
    '''
    
    def __init__(self,
                 name: str,
                 unit: str,
                 minimize: bool,
                 description: str,
                 symbol:str,
                 ip: str,
                 port: str,
                 position_index: int,
                 output_key:str):
        '''
        Initialize an objective definition.

        Args:
            
            name : str
                Internal identifier of the objective.
            
            unit : str
                Physical unit of the objective value.
            
            minimize : bool
                True if the objective must be minimized, False if maximized.
            
            description : str
                Human-readable description of the objective.
            
            symbol : str
                Symbol used in UI or scientific representation.
            
            ip : str
                IP address of the measurement source.
            
            port : str
                Port of the measurement source.
            
            position_index : int
                Position of the objective in ordered structures (UI / vector).
            
            output_key : str
                Key expected in the received payload for this objective.
        '''

        self.name = name
        self._unit = unit
        self._minimize = minimize

        self.description = description
        self.symbol = symbol

        self.ip = ip
        self.port = port

        self.position_index = position_index

        self.output_key = output_key
    
    @property
    def minimize(self) -> bool:
        return self._minimize
    
    @property
    def ip_port(self) -> str:
        return f"{self.ip}:{self.port}"

    @property
    def address(self) -> str:
        return self.ip_port
    
    @property
    def unit(self) -> str:
        return self._unit
    

    def set_minimize(self, minimize: bool) -> None:
        '''Update the optimization direction.'''
        self._minimize = minimize


    def __repr__(self):
        '''Compact representation.'''
        return (
            f"<{self.__class__.__name__}"
            f"(name='{self.name}', "
            f"minimize='{self.minimize}', "
            f"unit='{self.unit}'), "
            f"address={self.address}), "
            f"position index={self.position_index}>"
        )