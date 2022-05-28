from genericpath import exists
from arguments.FileLikeArgument import FileLikeArgument
from os.path import join, realpath
from os import environ


class IDWithFiletypeArgument(FileLikeArgument):
	id: str
	# An upper case string.
	ft: str

	def __init__(self, id_with_filetype: str):
		id, filetype = id_with_filetype.split(".", 1)
		self.id = id
		self.ft = filetype.upper()

	def __str__(self):
		return f"{self.id}.{self.ft}"
	
	def as_full_file_paths(self):
		path = join(
			environ.get("HOME"),
			"Documents",
			"Files",
			f"{self.id}.{self.ft}"
		)
		return realpath(path) if exists(path) else path

	def as_full_metadata_path(self):
		path = join(
			environ.get("HOME"),
			"Documents",
			"FileInfo",
			f"{self.id}.json"
		)
		return realpath(path) if exists(path) else path

	def as_full_annotations_path(self):
		path = join(
			environ.get("HOME"),
			"Documents",
			"FileAnnotations",
			f"{self.id}.json"
		)
		return realpath(path) if exists(path) else path

	def as_id(self):
		return self.id

	def as_filetypes(self):
		return {self.ft}