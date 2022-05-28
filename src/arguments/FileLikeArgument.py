from abc import abstractmethod
from typing import Optional, Set, Type
from arguments.Argument import Argument
from os.path import basename

from file_types.FileType import FileType


class FileLikeArgument(Argument):
	@abstractmethod
	def as_full_file_paths(self) -> Set[str]:
		return {}

	def as_full_typed_file_path(self, ft: Type[FileType]):
		return (
			list(self.as_full_file_paths())[0]
			if ft.applies_to_any_suffix(self.as_filetypes())
			else None
		)

	@abstractmethod
	def as_full_metadata_path(self) -> Optional[str]:
		return None

	@abstractmethod
	def as_full_annotations_path(self) -> Optional[str]:
		return None

	@abstractmethod
	def as_id(self):
		pass

	def parse_argument_for_action(self, _, current_index, action):
		action.file_arguments.append(self)
		return current_index + 1

	def as_filetypes(self):
		filetypes = set()
		for path in self.as_full_file_paths():
			split_basename = basename(path).split(".", 1)
			if len(split_basename) == 2:
				filetypes.add(split_basename[1].upper())

		return filetypes