import os
from actions.Action import Action
from os.path import exists
import subprocess


class EditNote(Action):
	@classmethod
	def command(cls) -> str:
		return "edit-note"

	@classmethod
	def description(cls):
		return "edit a note related to the file"

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
			note_path = fa.as_full_file_note_path()
			if not exists(note_path):
				with open(note_path, "w") as f:
					f.write(f"# Notes on {fa.as_id()[:10]}\n\n")
			subprocess.call(
				["/usr/bin/xdg-open", note_path],
				stderr=subprocess.DEVNULL
			)
			arguments = ["nohup", "/usr/bin/vim", note_path, "&"]
			subprocess.Popen(
				" ".join(arguments),
				stderr=subprocess.DEVNULL,
				shell=True,
				preexec_fn=os.setpgrp
			)