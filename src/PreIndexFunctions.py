import re
from typing import List, Dict

class PreIndexFunctions:
	def parsed_authors_to_strings(authors: List[Dict[str, str]]) -> str:
		if type(authors) == dict:
			s = authors["name"]
			if "email" in authors:
				s += " " + authors["email"]
			if "address" in authors:
				s += "\n" + "\n".join(authors["address"])
			return [s]
		if type(authors) == list:
			return [
				string
				for author in authors
				for strings in PreIndexFunctions.parsed_authors_to_strings(author)
				for string in strings
			]

	def pre_index_original_path(original_path) -> str:
		return " ".join([
			original_path,
			*re.split("/+", re.sub("^/+", "", original_path))
		])