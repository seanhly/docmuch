from arguments.FileLikeArgument import FileLikeArgument
from os.path import join, exists, realpath
from os import environ
from os import listdir
import re


class IDArgument(FileLikeArgument):
	id: str

	def __init__(self, id: str, _ = None):
		self.id = id

	def __str__(self):
		return self.id

	def as_full_file_paths(self):
		path = realpath(join(
			environ.get("HOME"),
			"Documents",
			"Files",
		))
		return {
			join(path, f)
			for f in listdir(path)
			if f[:40] == self.as_id()
		}
	
	def as_full_typed_file_path(self, ft):
		if not ft.suffixes():
			return list(self.as_full_file_paths())[0]
		else:
			for suffix in ft.suffixes():
				full_path = realpath(join(
					environ.get("HOME"),
					"Documents",
					"Files",
					f"{self.as_id()}.{suffix}"
				))
				if exists(full_path):
					return realpath(full_path)
		return None

	def as_full_metadata_path(self):
		dir = realpath(join(
			environ.get("HOME"),
			"Documents",
			"FileInfo",
		))
		return join(dir, f"{self.as_id()}.json")

	def as_full_annotations_path(self):
		dir = realpath(join(
			environ.get("HOME"),
			"Documents",
			"FileAnnotations",
		))
		return join(dir, f"{self.as_id()}.json")

	def as_full_file_note_path(self):
		dir = realpath(join(
			environ.get("HOME"),
			"Documents",
			"Notes",
		))
		return join(dir, f"{self.as_id()}.MD")
	
	def as_id(self):
		return self.id
	
	@classmethod
	def fits(cls, s: str) -> bool:
		return re.fullmatch("[0-9a-f]{40}", s)
