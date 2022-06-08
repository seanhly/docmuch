from actions.Action import Action
from os.path import exists
import subprocess
import os
from file_types.FileType import FileType
from arguments.PathArgument import PathArgument


class Open(Action):
	@classmethod
	def command(cls) -> str:
		return "open"

	@classmethod
	def description(cls):
		return "open the file"

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
			for path in fa.as_full_file_paths():
				inner_fa = PathArgument(path, action=self.command())
				for t in FileType.__subclasses__():
					if t.applies_to_fa(inner_fa):
						program = " ".join([
							"nohup",
							t.view_cmd(),
							t.view_path(inner_fa),
							"&",
						])
						print(program)
						subprocess.Popen(
							program,
							stderr=subprocess.DEVNULL,
							stdout=subprocess.DEVNULL,
							shell=True,
                 			preexec_fn=os.setpgrp
						)
