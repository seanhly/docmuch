import json
from file_types.FileType import FileType
from typing import Dict


class Recipe(FileType):
	@classmethod
	def get_info(cls, file):
		with open(file, "r") as f:
			content = f.read().strip()
			return json.loads(content)

	@classmethod
	def key(cls):
		return "recipe"

	@classmethod
	def required_fields(cls):
		return set()


	@classmethod
	def required_exif_mappings(cls) -> Dict[str, str]:
		return {}

	@classmethod
	def suffixes(cls):
		return {"RECIPE"}