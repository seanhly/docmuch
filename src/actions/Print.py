from actions.Action import Action
#from os.path import exists
import subprocess

from file_types.PDF import PDF


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
		for fa in self.file_arguments:
			lp = subprocess.Popen(
				[
					"/usr/bin/lp",
					"-n",
					str(1),
					fa.as_full_typed_file_path(PDF),
				]
			)
			lp.wait()