# libraries
import pathlib
import json
import re
from datetime import date

from laplace_log import log

# project
from .json_encoder import OptimizationJSONEncoder
from .model_form import is_date_folder


def save_opt_form(opt_form: dict) -> bool:
    '''
    Function made to save a dictionary optimization 
    form as a json file. Assumes the optimization form
    is correct, including a 'saving_path' entry in the 'exec' 
    dictionary indicating if and where the form should be saved.
    Return a boolean indicating if the configuration was saved.
    '''
    execution = opt_form.get("exec", {})
    saving_path_str = execution.get("saving_path")  # get the saving path from the execution dictionary
    
    if not saving_path_str: # if there is no saving_path
        return False        # do not save
    
    # make an absolute user path
    base_path = pathlib.Path(saving_path_str).expanduser().resolve()
    try:
        base_path.mkdir(parents=True, exist_ok=True)  # create the directory
    except Exception as e:
        raise RuntimeError(f"Invalid saving_path: {base_path}") from e

    if is_date_folder(base_path):  # if the path contains a 'yyyy-mm-dd' expression
        date_folder = base_path    # use the current path
    else:                          # else
        date_folder = base_path / date.today().isoformat() # add today in path name
        date_folder.mkdir(exist_ok=True)                   # create the today folder

    json_folder = date_folder / "save_config_json" 
    if not json_folder.exists():
        json_folder.mkdir(exist_ok=True)

    index = get_next_optimization_index(json_folder)  # get the index optimization form

    filename = f"optimization_form_{index:06d}.json"  # json file name
    output_file = json_folder / filename

    with output_file.open("w", encoding="utf-8") as f:  # write the file
        json.dump(opt_form, f, indent=4, cls=OptimizationJSONEncoder) # using 'OptimizationJSONEncoder' for classes
    
    log.info(f"Configuration saved to: '{output_file}'")
    return True  # the file was saved


def get_next_optimization_index(folder: pathlib.Path) -> int:
    '''
    Given a folder path, return the index of the next
    'optimization_form_******.json'.
    '''
    pattern = re.compile(r"optimization_form_(\d+)\.json") # load the patern

    indices = []
    for file in folder.glob("optimization_form_*.json"): # for each file
        match = pattern.fullmatch(file.name)             # make the match
        if match:                                        # if match
            indices.append(int(match.group(1)))          # increment the index (last element)

    return max(indices, default=0) + 1