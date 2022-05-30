from constants import DB_PATH
from third_party_modules import xapian
from urllib import request as request
from actions.Action import Action
from os import unlink
from os.path import exists


class Delete(Action):
	@classmethod
	def command(cls) -> str:
		return "delete"

	@classmethod
	def description(cls):
		return "delete the file and all its related metadata"

	def recognised_options(self):
		return set()

	def arg_options(self):
		return set()

	def obligatory_option_groups(self):
		return []

	def blocking_options(self):
		return []
	
	def execute(self) -> None:
		for fa in self.file_arguments:
			db = xapian.WritableDatabase(DB_PATH, xapian.DB_CREATE_OR_OPEN)
			file_id = fa.as_id()
			metadata = fa.as_full_metadata_path()
			file_paths = fa.as_full_file_paths()
			db.delete_document(file_id)
			if exists(metadata):
				unlink(metadata)
			for path in file_paths:
				if exists(path):
					unlink(path)
			print(f"file {file_id} deleted.")