from file_types.FileType import FileType
from typing import Set


class HTML(FileType):
	@classmethod
	def to_text(cls, fa):
		return None

	@classmethod
	def key(cls):
		return "html"

	@classmethod
	def suffixes(cls) -> Set[str]:
		return {"HTML", "HTM", "XHTML"}

	@classmethod
	def required_exif_mappings(cls):
		return {}

	@classmethod
	def non_keys(cls) -> Set[str]:
		return {
			"book",
			"tei",
			"image",
			"music",
		}

	@classmethod
	def required_fields(cls):
		return set()