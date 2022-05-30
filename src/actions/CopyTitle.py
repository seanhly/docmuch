from actions.Action import Action


class CopyTitle(Action):
	@classmethod
	def command(cls) -> str:
		return "copy-title"

	def recognised_options(self):
		return set()
	
	@classmethod
	def description(cls):
		return "copy the file's title"

	def arg_options(self):
		return set()

	def obligatory_option_groups(self):
		return []

	def blocking_options(self):
		return []
	
	def execute(self) -> None:
		pass