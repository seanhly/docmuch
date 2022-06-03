import os
from actions.Action import Action
from os.path import exists
import subprocess
from JSON import JSON


class Annotate(Action):
	@classmethod
	def command(cls) -> str:
		return "annotate"

	@classmethod
	def description(cls):
		return "manually edit metadata for the file"

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
			metadata_path = fa.as_full_annotations_path()
			if not exists(metadata_path):
				with open(metadata_path, "w") as f:
					JSON.dump(dict(
						title=None,
						creators=None,
					), f)
			arguments = ["nohup", "/usr/bin/gvim", metadata_path, "&"]
			print(" ".join(arguments))
			subprocess.Popen(
				" ".join(arguments),
				stderr=subprocess.DEVNULL,
				shell=True,
				preexec_fn=os.setpgrp
			)

