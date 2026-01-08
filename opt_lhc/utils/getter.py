# libraries
from pathlib import Path
import importlib.util
import inspect

# project
    # in / out
from model_construction.inputs.input_structure import InputStructure
from model_construction.objectives.objective_structure import ObjectiveStructure
    # init
from model_construction.initializations.initialization_structure import InitializationStructure
    # pipeline
from model_construction.strategies.strategy_structure import StrategyStructure
from model_construction.acquisitions.acquisition_structure import AcquisitionStructure


def get_classes(category: str) -> dict[str, type]:
    '''
    Get a dictionary {class_name, class} of every class
    contained in the 'model_construction/category' folder.
    '''
    # folder path
    dir = Path(__file__).parent.parent / "model_construction" / category
    
    result: dict[str, type] = {} # {class_name: class}

    structure = get_structure(category) # structure class to use depending on the category

    for py in dir.glob("*.py"): # for every python file in this folder
        
        # load the module
        spec = importlib.util.spec_from_file_location(f"{category}.{py.stem}", py)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        
        for _, cls in inspect.getmembers(mod, inspect.isclass): # for every class in the module
            
            # if the class does have the same name as the file, is a subclass and not the parent (structure) class
            if cls.__module__ == mod.__name__ and issubclass(cls, structure) and cls is not structure:
                
                result[cls.__name__] = cls # add it to the dictionary
    
    return result


def check_category(category: str) -> None:
    '''
    Verify if the 'category' is among the available ones.
    '''
    available_categories = [
        "inputs",
        "objectives",
        "initializations",
        "strategies",
        "acquisitions",
    ]
    if category not in available_categories:
        raise ValueError(f"category '{category}' invalid."
                         f"must be chosen among '{available_categories}.")


def get_structure(category: str):
    '''
    Return the corresponding structure class 
    to use depending on the 'category'.
    '''
    check_category(category)
    if category == "inputs":
        structure = InputStructure
    elif category == "objectives":
        structure = ObjectiveStructure
    elif category == "initializations":
        structure = InitializationStructure
    elif category == "strategies":
        structure = StrategyStructure
    elif category == "acquisitions":
        structure = AcquisitionStructure
    return structure