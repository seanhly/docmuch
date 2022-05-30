from arguments.FileLikeArgument import FileLikeArgument
from os.path import join, exists, realpath
from os import environ
from os import listdir
from arguments.IDArgument import IDArgument


class IDPrefixArgument(IDArgument):
	id_prefix: str

	def __init__(self, id_prefix: str, _ = None):
		self.id_prefix = id_prefix

	def __str__(self):
		return f"{self.id_prefix}*"
	
	def as_id(self):
		files_dir = realpath(join(
			environ.get("HOME"),
			"Documents",
			"Files",
		))
		for f in listdir(files_dir):
			if f[:len(self.id_prefix)] == self.id_prefix:
				return f.split(".", 1)[0]

		return None