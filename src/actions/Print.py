from actions.Action import Action
#from os.path import exists
#import subprocess


class Print(Action):
	@classmethod
	def command(cls) -> str:
		return "print"

	@classmethod
	def description(cls):
		return "print files"

	def recognised_options(self):
		return set()

	def arg_options(self):
		return set()

	def obligatory_option_groups(self):
		return []

	def blocking_options(self):
		return []
	
	def execute(self) -> None:
		raise ValueError("""
			Printing things via docmuch is not yet supported.
		""")