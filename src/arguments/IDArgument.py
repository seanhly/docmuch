from arguments.FileLikeArgument import FileLikeArgument
from os.path import join, exists, realpath
from os import listdir
from constants import FILES_PATH
import re
from typing import Dict, List


id_index: Dict[str, List[str]] = None


class IDArgument(FileLikeArgument):
	id: str

	def __init__(self, id: str, _ = None):
		self.id = id

	def __str__(self):
		return self.as_id()

	def as_full_file_paths(self):
		global id_index
		if not id_index:
			id_index = {}
			for f in listdir(FILES_PATH):
				id, suffix = f.split(".")
				id_index[id] = id_index.get(id, []) + [suffix]
		return {
			join(FILES_PATH, f"{self.as_id()}.{suffix}")
			for suffix in id_index[self.as_id()]
		}
	
	def as_full_typed_file_path(self, ft):
		if not ft.suffixes():
			return list(self.as_full_file_paths())[0]
		else:
			for suffix in ft.suffixes():
				full_path = realpath(join(
					FILES_PATH, f"{self.as_id()}.{suffix}",
				))
				if exists(full_path):
					return realpath(full_path)
		return None

	def as_id(self):
		return self.id
	
	@classmethod
	def fits(cls, s: str) -> bool:
		return re.fullmatch("[0-9a-f]{40}", s)
