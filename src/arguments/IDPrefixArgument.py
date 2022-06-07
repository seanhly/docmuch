from arguments.FileLikeArgument import FileLikeArgument
from os.path import join, exists, realpath
from os import environ
from os import listdir
from arguments.IDArgument import IDArgument
from typing import Optional
from constants import FILES_PATH


class IDPrefixArgument(IDArgument):
	id_prefix: str

	def __init__(self, id_prefix: str, _ = None):
		self.id_prefix = id_prefix
		self.id = None

	def __str__(self):
		if self.id:
			return self.id
		return f"{self.id_prefix}*"
	
	def as_id(self):
		if not self.id:
			for f in listdir(FILES_PATH):
				if f[:len(self.id_prefix)] == self.id_prefix:
					self.id = f.split(".", 1)[0]
					break

		return self.id
