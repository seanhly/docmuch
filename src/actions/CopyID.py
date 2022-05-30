from actions.Action import Action
from actions.Parse import get_metadata
import json


class CopyID(Action):
	@classmethod
	def command(cls) -> str:
		return "copy-id"

	@classmethod
	def name(cls) -> str:
		return "Copy ID"

	def recognised_options(self):
		return set()
	
	@classmethod
	def description(cls):
		return "copy the file's ID"

	def arg_options(self):
		return set()

	def obligatory_option_groups(self):
		return []

	def blocking_options(self):
		return []
	
	def execute(self) -> None:
		pass