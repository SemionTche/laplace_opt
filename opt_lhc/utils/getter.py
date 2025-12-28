from pathlib import Path
import importlib.util
import inspect
from model_construction.inputs.input_structure import InputStructure
from model_construction.objectives.objective_structure import ObjectiveStructure
from model_construction.initializations.initialization_structure import InitializationStructure
from model_construction.models.model_structure import ModelStructure
from model_construction.acquisitions.acquisition_structure import AcquisitionStructure
from model_construction.fitters.fitter_structure import FitterStructure
from model_construction.samplers.sampler_structure import SamplerStructure

def get_classes(category: str) -> dict[str, type]:
    inputs_dir = Path(__file__).parent.parent / "model_construction" / category
    
    result: dict[str, type] = {}
    
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
    else:
        raise ValueError("The 'category' argument of 'get_classes' should be either 'inputs' or 'objectives'.")

    for py in inputs_dir.glob("*.py"):

        if py.name in ("__init__.py", "input_structure.py", "objective_structure.py"):
            continue
        
        spec = importlib.util.spec_from_file_location(f"{category}.{py.stem}", py)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        
        for _, cls in inspect.getmembers(mod, inspect.isclass):
            if cls.__module__ == mod.__name__ and issubclass(cls, structure) and cls is not structure:
                # choose display name here if you have one, else class.__name__
                result[cls.__name__] = cls
    
    return result


def get_from_cls(cls: type, attr: str):
    '''
    Get the 'attr' attribute from the 'cls' class argument.
    If the attribute is not found, return 'None'. Otherwise,
    return the attribute.
    '''
    try:
        # if there is no 'cls' class.
        if hasattr(cls, "default") and callable(getattr(cls, "default")):
            inst = cls.default() # creates the default instance
        else:
            inst = cls()         # else use the 'cls' instance
        val = getattr(inst, attr, None)  # if possible get the attribute value, else return None 
    except Exception: # if the process failed
        val = None # return None
    return val


# def get_input_class_names() -> List[str]:
#     """
#     Scan the 'inputs' folder and return class names or a specific class attribute.

#     Args:
#         return_attr: If None, return the class __name__; otherwise, return the class attribute value.

#     Returns:
#         List of class names or attribute values.
#     """
#     inputs_dir = Path(__file__).parent.parent / "inputs"
#     class_names: List[str] = []

#     for py in inputs_dir.glob("*.py"):
#         if py.name in ("__init__.py", "input_structure.py"):
#             continue

#         spec = importlib.util.spec_from_file_location(f"inputs.{py.stem}", py)
#         mod = importlib.util.module_from_spec(spec)
#         spec.loader.exec_module(mod)

#         for _, cls in inspect.getmembers(mod, inspect.isclass):
#             if cls.__module__ == mod.__name__ and issubclass(cls, InputStructure) and cls is not InputStructure:
#                     class_names.append(cls.__name__)

#     return class_names