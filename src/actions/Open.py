from actions.Action import Action
from os.path import exists
import subprocess
import os


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
			file_paths = fa.as_full_file_paths()
			for path in file_paths:
				print(path)
				if exists(path):
					arguments = ["nohup", "/usr/bin/xdg-open", path, "&"]
					subprocess.Popen(
						" ".join(arguments),
						stderr=subprocess.DEVNULL,
						shell=True,
                 		preexec_fn=os.setpgrp
					)
