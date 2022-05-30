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

	def as_full_metadata_path(self) -> str:
		path = realpath(self.path)
		files_path = realpath(join(environ.get("HOME"), "Documents", "Files"))
		file_info_path = realpath(join(environ.get("HOME"), "Documents", "FileInfo"))
		if self.movable:
			file_id = self.as_id()
			metadata_path = join(file_info_path, f"{file_id}.json")
		else:
			metadata_match = re.fullmatch(f"{file_info_path}/([0-9a-f]{{40}}).json", path)
			if metadata_match:
				metadata_path = path
			else:
				in_system_files_match = re.fullmatch(
					f"{files_path}/([0-9a-f]{{40}})(\.[a-zA-Z0-9]+)+", path
				)
				if in_system_files_match:
					metadata_path = f"{file_info_path}/{in_system_files_match[1]}.json"
				else:
					metadata_path = None

		return metadata_path

	def as_full_annotations_path(self):
		path = realpath(self.path)
		files_path = realpath(join(environ.get("HOME"), "Documents", "Files"))
		file_info_path = realpath(join(environ.get("HOME"), "Documents", "FileInfo"))
		file_annotations_path = realpath(join(environ.get("HOME"), "Documents", "FileAnnotations"))
		metadata_match = re.fullmatch(f"{file_info_path}/([0-9a-f]{{40}}).json", path)
		if metadata_match:
			annotations_path = f"{file_annotations_path}/{metadata_match[1]}.json"
		else:
			in_system_files_match = re.fullmatch(
				f"{files_path}/([0-9a-f]{{40}})(\.[a-zA-Z0-9]+)+", path
			)
			if in_system_files_match:
				annotations_path = f"{file_annotations_path}/{in_system_files_match[1]}.json"
			else:
				annotations_match = re.fullmatch(
					f"{file_annotations_path}/([0-9a-f]{{40}}).json", path
				)
				if annotations_match:
					annotations_path = path
				else:
					annotations_path = None

		return annotations_path
	
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

	def as_id(self) -> str:
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

		return the_id

	def as_full_file_note_path(self):
		notes_dir = realpath(join(
			environ.get("HOME"),
			"Documents",
			"Notes",
		))
		return join(notes_dir, f"{self.as_id()}.MD")

	@classmethod
	def fits(cls, s: str) -> bool:
		return Path(s).is_file()