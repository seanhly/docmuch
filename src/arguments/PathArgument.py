from pathlib import Path
from typing import List, Set, Tuple
from arguments.FileLikeArgument import FileLikeArgument
from os.path import realpath, join
from os import environ, stat
import re
from arguments.IDWithFiletypeArgument import IDWithFiletypeArgument
from constants import TYPICALLY_WRITE_ONCE_FILETYPES
import hashlib
import secrets


class PathArgument(FileLikeArgument):
	path: str
	movable: bool

	def __init__(self, path: str, action: str):
		self.path = path
		self.id = None
		self.movable = action in {"parse"}

	def __str__(self) -> str:
		return self.path

	def as_full_file_paths(self) -> Set[str]:
		return {realpath(self.path)}

	def as_full_file_destination(self):
		files_dir = realpath(join(
			environ.get("HOME"),
			"Documents",
			"Files",
		))

		return join(
			files_dir,
			f"{self.as_id()}.{list(self.as_filetypes())[0]}"
		)

	def needs_moving(self):
		id_like_strings = re.findall("[0-9a-f]{40}", self.path)
		if len(id_like_strings) == 1:
			for ft in self.as_filetypes():
				expected_fa = IDWithFiletypeArgument(f"{id_like_strings[0]}.{ft}")
				expected_paths = {
					expected_fa.as_full_annotations_path(),
					expected_fa.as_full_metadata_path(),
					*expected_fa.as_full_file_paths()
				}
				if not self.as_full_file_paths().isdisjoint(expected_paths):
					return False

		return True

	the_id = None
	def as_id(self) -> str:
		if self.the_id:
			return self.the_id
		id_like_strings = re.findall("[0-9a-f]{40}", self.path)
		the_id = None
		if len(id_like_strings) == 1:
			if self.movable or not self.needs_moving():
				the_id = id_like_strings[0]
		else:
			ids_by_file_size: List[Tuple[int, str]] = []
			for path in self.as_full_file_paths():
				file_size = stat(path).st_size
				"""
				For files above 50KB,
				you can also use the
				file hash as a key.
				"""
				if self.as_filetypes().issubset(
					TYPICALLY_WRITE_ONCE_FILETYPES
				) or file_size > 50000:
					with open(path, "rb") as f:
						ids_by_file_size.append((
							stat(path).st_size,
							hashlib.sha1(f.read()).hexdigest(),
						))
			if ids_by_file_size:
				the_id = sorted(ids_by_file_size)[-1][1]
			else:
				"""
				Fallback to a random
				ID for smaller
				documents, with no SHA
				key candidate files.
				"""
				the_id = secrets.token_hex(20)

		self.the_id = the_id
		return the_id

	@classmethod
	def fits(cls, s: str) -> bool:
		return Path(s).is_file()