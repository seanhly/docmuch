from typing import Optional
from actions.Action import Action
from arguments.Argument import Argument
import re
from arguments.OtherArgument import OtherArgument


class TagArgument(Argument):
	# Does the tag belong to the thing, or does it not?
	polarity: bool
	# The name of the tag.
	name: str

	def __init__(self, name: Optional[str] = None, polarity: Optional[bool] = None) -> None:
		if polarity is not None:
			self.polarity = polarity
			self.name = name
		elif name[0] == "+":
			self.polarity = True
			self.name = name
		elif name[0] == "-":
			self.polarity = False
			self.name = name
		else:
			self.polarity = True
			self.name = name

	def __str__(self) -> str:
		return self.name

	def parse_argument_for_action(self, arguments, current_index, action: Action):
		if action.command() == "tag" and current_index == 0:
			action.tag = self
			next_index = current_index + 1
		elif self.polarity:
			next_index = OtherArgument(
				f"+{self.argument}"
			).parse_argument_for_action(arguments, current_index, action)
		else:
			arguments.insert
			current_index.arguments
			action.query_parts.append("NOT")
			next_index = OtherArgument(self.name).parse_argument_for_action(arguments, current_index, action)
		return next_index

	@classmethod
	def fits(cls, s: str) -> bool:
		return re.fullmatch("[+-].*", s)