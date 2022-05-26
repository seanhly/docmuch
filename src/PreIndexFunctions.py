import re
from typing import List, Dict

class PreIndexFunctions:
	def parsed_authors_to_strings(authors: List[Dict[str, str]], sep="\n") -> str:
		if type(authors) == dict:
			s = authors["name"]
			if "email" in authors:
				s += " " + authors["email"]
			if "address" in authors:
				s += sep + sep.join(authors["address"])
			return [s]
		if type(authors) == list:
			return [
				string
				for author in authors
				for string in PreIndexFunctions.parsed_authors_to_strings(author, sep=sep)
			]

	def pre_index_original_path(original_path) -> str:
		return " ".join([
			original_path,
			*re.split("/+", re.sub("^/+", "", original_path))
		])
