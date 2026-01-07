# libraries
import pathlib
import json
import re
from datetime import date, datetime

# project
from utils.json_encoder import OptimizationJSONEncoder


def save_config(opt_form: dict):
    execution = opt_form.get("exec", {})
    saving_path_str = execution.get("saving_path")
    if not saving_path_str:
        return False
    
    base_path = pathlib.Path(saving_path_str).expanduser().resolve()
    try:
        base_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise RuntimeError(f"Invalid saving_path: {base_path}") from e
    
    if not base_path.is_dir():
        raise ValueError(f"saving_path is not a directory: {base_path}")

    # if is_date_folder(base_path) and base_path.name != date.today().isoformat():
    #     raise ValueError("Saving into a past date folder is not allowed")

    if is_date_folder(base_path):
        date_folder = base_path
    else:
        date_folder = base_path / date.today().isoformat()
        date_folder.mkdir(exist_ok=True)

    index = get_next_optimization_index(date_folder)

    filename = f"optimization_form_{index:06d}.json"
    output_file = date_folder / filename

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(opt_form, f, indent=4, cls=OptimizationJSONEncoder)
    
    print(f"Configuration saved to {output_file}")
    return True


def get_next_optimization_index(folder: pathlib.Path) -> int:
    pattern = re.compile(r"optimization_form_(\d+)\.json")

    indices = []
    for file in folder.glob("optimization_form_*.json"):
        match = pattern.fullmatch(file.name)
        if match:
            indices.append(int(match.group(1)))

    return max(indices, default=0) + 1



def is_date_folder(path: pathlib.Path) -> bool:
    try:
        datetime.strptime(path.name, "%Y-%m-%d")
        return True
    except ValueError:
        return False