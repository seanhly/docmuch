from arguments.FileLikeArgument import FileLikeArgument
from os.path import join, exists, realpath
from os import environ
from os import listdir

from file_types.FileType import FileType


class IDArgument(FileLikeArgument):
	id: str

	def __init__(self, id: str):
		self.id = id

	def __str__(self):
		return self.id

	def as_full_file_paths(self):
		files_path = join(
			environ.get("HOME"),
			"Documents",
			"Files",
		)
		return {
			join(files_path, f)
			for f in listdir(files_path)
			if f[:40] == self.id
		}
	
	def as_full_typed_file_path(self, ft):
		if not ft.suffixes():
			return list(self.as_full_file_paths())[0]
		else:
			for suffix in ft.suffixes():
				full_path = join(
					environ.get("HOME"),
					"Documents",
					"Files",
					f"{self.id}.{suffix}"
				)
				if exists(full_path):
					return realpath(full_path)
		return None

	def as_full_metadata_path(self):
		path = join(
			environ.get("HOME"),
			"Documents",
			"FileInfo",
			f"{self.id}.json"
		)
		return realpath(path) if exists(path) else path

	def as_full_annotations_path(self):
		return join(
			environ.get("HOME"),
			"Documents",
			"FileAnnotations",
			f"{self.id}.json"
		)
	
	def as_id(self):
		return self.id