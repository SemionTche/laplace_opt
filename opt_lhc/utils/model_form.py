# libraries
from enum import Enum
from datetime import datetime, date
import pathlib

# project
from model_construction.inputs.input_structure import InputStructure
from model_construction.objectives.objective_structure import ObjectiveStructure
from model_construction.initializations.initialization_structure import InitializationStructure
from model_construction.strategies.strategy_structure import StrategyStructure
from model_construction.acquisitions.acquisition_structure import AcquisitionStructure

StratOrAcq = StrategyStructure | AcquisitionStructure


class ValidationLevel(Enum):
    '''Helping class to define validation state.'''
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"


def is_date_folder(path: pathlib.Path) -> bool:
    '''
    Helper that return True if there is a 'yyyy-mm-dd' expression
    in the given path and False otherwise.
    '''
    try:
        datetime.strptime(path.name, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def make_form(exec: dict[str, bool | str], 
              inputs: dict[str, InputStructure], 
              obj: dict[str, ObjectiveStructure], 
              init: dict[str, InitializationStructure | dict[str, int | float | bool | str]], 
              opt: dict[str, bool | dict[str, dict[str, StratOrAcq | dict[str, int | float | bool | str]]]]
            ) -> tuple[dict, tuple[ValidationLevel, str]]:
    '''
    Create the form dictionary of an optimization.
    '''
    # add current date and time to the optimization form
    now = datetime.now()
    saved_date = now.date().isoformat()
    saved_time = now.time().isoformat(timespec="seconds")

    form = {
        "saved_date": saved_date,
        "saved_time": saved_time,
        "exec": exec,
        "inputs": inputs,
        "obj": obj,
        "init": init,
        "opt": opt
    }
    
    validation = check_form(form)

    return form, validation


def check_form(form: dict) -> tuple[ValidationLevel, str]:
    '''
    Verify the dictionary given in argument for an optimization.
    '''
    inputs = form["inputs"]
    if len(inputs) < 1:
        return ValidationLevel.ERROR, "At least one input must be selected."

    opt = form["opt"]
    if opt["enabled"] is True:
        objectives = form["obj"]
        if len(objectives) < 1:
            return (
                ValidationLevel.ERROR,
                "When optimizing, at least one objective must be selected."
            )

    execution = form["exec"]

    # saving_path warning / error
    saving_path = execution.get("saving_path", "")
    if saving_path == "":
        parts: list[str] = []

        # initialization
        init_dict = form["init"]
        # init_data = next(iter(init_dict.values()), None)

        if init_dict is not None:
            init_cls = init_dict["cls"]
            if not init_cls.__name__.endswith("FileInitialization"):
                parts.append("the initialization")

        # optimization
        if opt["enabled"]:
            parts.append("the optimization")

        if parts:
            msg = (
                "No saving path registered. "
                + " and ".join(parts)
                + " will not be saved."
            )
        else:
            return (
                ValidationLevel.ERROR,
                "No action is required. Please enable at least an initialization or an optimization.",
            )

        return ValidationLevel.WARNING, msg

    path = pathlib.Path(saving_path).expanduser() # making a user path
    if is_date_folder(path):                      # if there is a 'yyyy-mm-dd' patern in the path
        today = date.today().isoformat()          # get today
        if path.name != today:                    # if the date patern does not correspond
            return (                              # make a warning
                ValidationLevel.WARNING,
                f"The saving path points to a past date folder ({path.name}). "
                f"Results will be saved in that folder instead of today's ({today})."
            ) 

    return ValidationLevel.OK, ""