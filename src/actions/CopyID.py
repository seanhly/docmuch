from actions.Action import Action


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
		import subprocess
		for source in (
			"buffer-cut",
			"clipboard",
			"primary",
			"secondary",
		):
			xclip_arguments = ["/usr/bin/xclip", "-selection", source]
			xclip = subprocess.Popen(xclip_arguments, stdin=subprocess.PIPE)
			for fa in self.file_arguments:
				xclip.stdin.write(bytes(f"{fa.as_id()}\n", encoding="utf8"))
			xclip.stdin.close()
			xclip.wait()