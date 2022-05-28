from actions.Action import Action
from actions.Parse import get_metadata
import json


class Debug(Action):
	@classmethod
	def command(cls) -> str:
		return "debug"

	def recognised_options(self):
		return set()

	def arg_options(self):
		return set()

	def obligatory_option_groups(self):
		return []

	def blocking_options(self):
		return []
	
	def execute(self) -> None:
		paths = [
			path
			for f in self.file_arguments
			for path in f.as_full_file_paths()
		]
		print(
			json.dumps(
				get_metadata(paths),
				separators=(",", ":"),
			)
		)