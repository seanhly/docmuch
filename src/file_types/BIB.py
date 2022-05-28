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
	def get_info(cls, fa):
		bib_info = {}
		with open(fa.as_full_typed_file_path(cls), "r") as f:
			content = f.read().strip().replace("\n", " ")
			for key in BIB_KEYS:
				pattern = f"\s{key}\s*=\s*(.*?)" + "\},"
				items = [
					match.strip()
					for match in re.findall(pattern, content)
				]
				if items:
					bib_info[key] = re.sub(
						"^\s+", "",
						re.sub(
							"\s+$", "",
							re.sub(
								"(\s|[{}])+",
								" ",
								" ".join(items)
							)
						)
					)
		#print(bib_info)
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
