import re
from file_types.FileType import FileType

BIB_KEYS = [
	"year", "author", "title", "publisher", "pages", "journal", "volume",
	"address", "number", "edition", "booktitle", "note", "series",
	"urldate", "month", "editor", "chapter", "howpublished", "url",
	"school", "place", "organization", "location", "institution"
]


class BIB(FileType):
	@classmethod
	def get_info(cls, file):
		bib_info = {}
		with open(file, "r") as f:
			content = f.read().strip()
			for key in BIB_KEYS:
				pattern = "(^|\n)\s*" + key + "\s*=\s*[{\"'](.*)[}\"']\s*,?\s*(\n|$)"
				items = [
					matches[1].strip()
					for matches in re.findall(pattern, content)
				]
				if items:
					bib_info[key] = "\n".join(items)
		return bib_info

	@classmethod
	def key(cls):
		return "bib"

	@classmethod
	def required_exif_mappings(cls):
		return {}

	@classmethod
	def non_keys(cls):
		return {
			"recipe",
			"song",
		}

	@classmethod
	def required_fields(cls):
		return set()


	@classmethod
	def suffixes(cls):
		return {"BIB"}