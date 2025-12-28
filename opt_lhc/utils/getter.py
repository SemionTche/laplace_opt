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
from model_construction.models.model_structure import ModelStructure
from model_construction.acquisitions.acquisition_structure import AcquisitionStructure
from model_construction.fitters.fitter_structure import FitterStructure
from model_construction.samplers.sampler_structure import SamplerStructure


def get_classes(category: str) -> dict[str, type]:
    '''
    Get a dictionary {class_name, class} of every class
    contained in the 'model_construction/category' folder.
    '''
    # folder path
    dir = Path(__file__).parent.parent / "model_construction" / category
    
    result: dict[str, type] = {}

    structure = get_structure(category) # class to use depending on the category

    for py in dir.glob("*.py"): # for every python file in this folder

        if py.name in ("__init__.py", "input_structure.py", "objective_structure.py"):
            continue
        
        # load the module
        spec = importlib.util.spec_from_file_location(f"{category}.{py.stem}", py)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        
        for _, cls in inspect.getmembers(mod, inspect.isclass): # for every class in the module
            
            # if the class does have the same name as the file, is a subclass and not the parent (structure) class
            if cls.__module__ == mod.__name__ and issubclass(cls, structure) and cls is not structure:
                
                result[cls.__name__] = cls # add it to the dictionary
    
    return result


def get_from_cls(cls: type, attr: str):
    '''
    Get the 'attr' attribute from the 'cls' class argument.
    If the attribute is not found, return 'None'. Otherwise,
    return the attribute.
    '''
    try:
        return getattr(cls(), attr, None)  # if possible get the attribute value, else return None
    except TypeError:                      # except if the instance failed
        return None                        # return None


def verify_category(category: str):
    '''
    Check if the 'category' is among the available ones.
    '''
    available_categories = [
        "inputs",
        "objectives",
        "initializations",
        "models",
        "acquisitions",
        "fitters",
        "samplers"
    ]
    if category not in available_categories:
        raise ValueError(f"category '{category}' invalid."
                         f"must be chosen among '{available_categories}.")


def get_structure(category: str):
    '''
    Return the corresponding structure class 
    to use depending on the category.
    '''
    verify_category(category)
    if category == "inputs":
        structure = InputStructure
    elif category == "objectives":
        structure = ObjectiveStructure
    elif category == "initializations":
        structure = InitializationStructure
    elif category == "models":
        structure = ModelStructure
    elif category == "acquisitions":
        structure = AcquisitionStructure
    elif category == "fitters":
        structure = FitterStructure
    elif category == "samplers":
        structure = SamplerStructure
    return structure