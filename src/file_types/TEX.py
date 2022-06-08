from urllib import request as request
import subprocess
import re
from file_types.FileType import FileType
from constants import DETEX_CMD


class TEX(FileType):
	@classmethod
	def to_text(cls, fa):
		return subprocess.check_output(
			[DETEX_CMD, fa.as_full_typed_file_path(cls)]
		).decode().strip()

	@classmethod
	def get_info(cls, fa):
		tex_info = {}
		with open(fa.as_full_typed_file_path(cls), "r") as f:
			content = f.read().strip()
			authors = re.findall("\\\\(?:author|signature)\{([^\}]*)\}", content)
			if authors:
				tex_info["author"] = re.split(
					" *\\\\ *",
					re.sub("\\s+", " ", authors[0]).strip()
				)[0]
			titles = re.findall("\\\\title\{([^\}]*)\}", content)
			if titles:
				tex_info["title"] = re.sub("\\s+", " ", titles[0]).strip()

		return tex_info

	@classmethod
	def key(cls):
		return "tex"

	@classmethod
	def required_exif_mappings(cls):
		return {}

	@classmethod
	def required_fields(cls):
		return set()

	@classmethod
	def suffixes(cls):
		return {"TEX"}

	@classmethod
	def view_cmd(cls) -> str:
		return "/usr/bin/lxterminal -e /usr/bin/vim"