from typing import List, Type
from arguments.Argument import Argument
from arguments.OtherArgument import OtherArgument
from arguments.OptionArgument import OptionArgument
from arguments.PathArgument import PathArgument
from arguments.IDArgument import IDArgument
from arguments.IDWithFiletypeArgument import IDWithFiletypeArgument
from arguments.TagArgument import TagArgument

def parse_dynamic_argument(argument: str, action: str):
	argument_types: List[Type[Argument]] = [
		PathArgument,
		IDArgument,
		IDWithFiletypeArgument,
		OptionArgument,
		TagArgument,
		OtherArgument,
		IDArgument,
	]
	for T in argument_types:
		if T.fits(argument):
			return T(argument, action)
	return None