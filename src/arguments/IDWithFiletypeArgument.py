from genericpath import exists
from arguments.FileLikeArgument import FileLikeArgument
from os.path import join, realpath
from os import environ
import re


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
		return {realpath(path) if exists(path) else path}

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

	def as_full_file_note_path(self):
		notes_dir = realpath(join(
			environ.get("HOME"),
			"Documents",
			"Notes",
		))
		return join(notes_dir, f"{self.id}.MD")

	def as_id(self):
		return self.id

	def as_filetypes(self):
		return {self.ft}

	@classmethod
	def fits(cls, s: str) -> bool:
		return re.fullmatch("[0-9a-f]{40}(\.[a-zA-Z0-9]+)+", s)