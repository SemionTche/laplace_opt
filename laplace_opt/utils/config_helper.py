# libraries
from pathlib import Path

from PyQt6.QtCore import QSettings

APP_CONFIG_PATH = Path(__file__).parent.parent / "app_config.ini"


def get_app_config():
    '''Return the app config settings'''
    settings = QSettings(
        str(APP_CONFIG_PATH), 
        QSettings.Format.IniFormat
    )
    return settings


def get_from_config(
        module: str, 
        item: str, 
        default_value: str | int = "", 
        type: type = str, 
        config_path: Path | str = APP_CONFIG_PATH):
    '''Get the 'item' stored in 'module' in the config file.'''
    
    settings = QSettings(
        str(config_path), 
        QSettings.Format.IniFormat
    )
    
    val = settings.value(
        f"{module}/{item}", 
        defaultValue=default_value, 
        type=type
    )

    return val


def set_in_config(
        module: str, 
        item: str, 
        val,
        config_path: Path | str = APP_CONFIG_PATH) -> None:
    '''Set the value of 'item' stored in 'module' in the config file.'''
    settings = QSettings(
        str(config_path), 
        QSettings.Format.IniFormat
    )

    settings.setValue(
        f"{module}/{item}",
        val
    )