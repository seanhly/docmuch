from os.path import exists
from urllib import request as request
import subprocess
import re
from file_types.FileType import FileType


class TEX(FileType):
	@classmethod
	def to_text(cls, file):
		CMD = '/usr/bin/detex'
		if not exists(CMD):
			raise RuntimeError('System command not found: %s' % CMD)
		if not exists(file):
			raise RuntimeError('Provided input file not found: %s' % file)
		return subprocess.check_output([CMD, file]).decode().strip()

	@classmethod
	def get_info(cls, file):
		tex_info = {}
		with open(file, "r") as f:
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
