from file_types.FileType import FileType
from typing import Set


class Plaintext(FileType):
	@classmethod
	def to_text(cls, file):
		with open(file, "r") as f:
			return f.read()

	@classmethod
	def key(cls):
		return "plaintext"

	@classmethod
	def suffixes(cls) -> Set[str]:
		return {"TXT", "MD", "ORG"}

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