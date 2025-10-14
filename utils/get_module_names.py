from pathlib import Path
import importlib.util
import inspect
from typing import List
from inputs.input_structure import InputStructure


def get_input_class_names() -> List[str]:
    """
    Scan the 'inputs' folder and return class names or a specific class attribute.

    Args:
        return_attr: If None, return the class __name__; otherwise, return the class attribute value.

    Returns:
        List of class names or attribute values.
    """
    inputs_dir = Path(__file__).parent.parent / "inputs"
    class_names: List[str] = []

    for py in inputs_dir.glob("*.py"):
        if py.name in ("__init__.py", "input_structure.py"):
            continue

        spec = importlib.util.spec_from_file_location(f"inputs.{py.stem}", py)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        for _, cls in inspect.getmembers(mod, inspect.isclass):
            if cls.__module__ == mod.__name__ and issubclass(cls, InputStructure) and cls is not InputStructure:
                    class_names.append(cls.__name__)

    return class_names
