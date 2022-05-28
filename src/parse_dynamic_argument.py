from arguments.OtherArgument import OtherArgument
from arguments.OptionArgument import OptionArgument
from arguments.PathArgument import PathArgument
from arguments.IDArgument import IDArgument
from arguments.IDWithFiletypeArgument import IDWithFiletypeArgument
from pathlib import Path
import re

def parse_dynamic_argument(argument: str, action: str):
    if Path(argument).is_file():
        parsed_argument = PathArgument(argument, movable=action in {"parse"})
    elif re.fullmatch("[0-9a-f]{40}", argument):
        parsed_argument = IDArgument(argument)
    elif re.fullmatch("[0-9a-f]{40}(\.[a-zA-Z0-9]+)+", argument):
        parsed_argument = IDWithFiletypeArgument(argument)
    elif re.fullmatch("--.*", argument):
        parsed_argument = OptionArgument(argument)
    else:
        parsed_argument = OtherArgument(argument)

    return parsed_argument