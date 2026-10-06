# libraries
from pathlib import Path
import importlib.util
import inspect

# project
from ..model_construction import (
    InputStructure, ObjectiveStructure,
    AcquisitionStructure, StrategyStructure,
    InitializationStructure, CriteriumStructure
)
from ..utils.model_source import ModelSource


def get_classes(dir: Path, category: str) -> dict[str, type]:
    '''
    Get a dictionary {class_name, class} of every class
    contained in the 'model_construction/category' folder.
    '''
    # folder path
    # dir = Path(__file__).parent.parent / "model_construction" / category
    dir = dir / category

    result: dict[str, type] = {} # {class_name: class}

    structure = get_structure(category) # structure class to use depending on the category
    
    
    for py in dir.glob("*.py"): # for every python file in this folder
        
        # load the module
        spec = importlib.util.spec_from_file_location(
            f"{category}.{py.stem}", 
            py
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        
        for _, cls in inspect.getmembers(mod, inspect.isclass): # for every class in the module
            
            # if the class does have the same name as the file, is a subclass and not the parent (structure) class
            if (
                cls.__module__ == mod.__name__ 
                and issubclass(cls, structure) 
                and cls is not structure ):
                
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
        raise ValueError(f"category '{category}' invalid.\n"
                         f"Must be chosen among '{available_categories}.")


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


def get_criterium_cls(source: ModelSource) -> CriteriumStructure:
    '''
    Load and return the CriteriumStructure class from the
    model_construction/criterium folder.
    '''
    folder = source.criterium

    files = list(folder.glob("*.py"))

    if len(files) != 1:
        raise ValueError(
            f"Expected exactly one Python file in '{folder}', "
            f"found {len(files)}."
        )

    py = files[0]

    spec = importlib.util.spec_from_file_location(
        f"criterium.{py.stem}",
        py
    )

    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from '{py}'.")

    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    cls = getattr(mod, "CriteriumStructure", None)

    if cls is None or not inspect.isclass(cls):
        raise TypeError(
            f"'CriteriumStructure' class not found in '{py}'."
        )

    return cls