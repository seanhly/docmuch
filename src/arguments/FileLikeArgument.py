from abc import abstractmethod
from os import environ, listdir
from typing import Set, Type
from arguments.Argument import Argument
from os.path import basename, join, realpath
import re
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

	def as_full_metadata_path(self) -> str:
		metadata_dir = realpath(join(
			environ.get("HOME"),
			"Documents",
			"FileInfo",
		))

		return join(metadata_dir, f"{self.as_id()}.json")
	
	def as_full_annotations_path(self):
		annotations_dir = realpath(join(
			environ.get("HOME"),
			"Documents",
			"FileAnnotations",
		))

		return join(annotations_dir, f"{self.as_id()}.json")
	
	def as_full_file_note_path(self):
		notes_dir = realpath(join(
			environ.get("HOME"),
			"Documents",
			"Notes",
		))
		return join(notes_dir, f"{self.as_id()}.MD")

	@abstractmethod
	def as_id(self):
		pass

	def parse_argument_for_action(self, _, current_index, action):
		action.file_arguments.append(self)
		return current_index + 1

	def as_filetypes(self):
		filetypes = set()
		for path in self.as_full_file_paths():
			split_basename = re.split(
				FileType.valid_suffix_pattern(),
				basename(path).upper(),
			)
			if len(split_basename) == 2:
				filetypes.add(split_basename[1].upper())

		return filetypes

	def shortest_id_prefix(self):
		files_dir = realpath(join(
			environ.get("HOME"),
			"Documents",
			"Files",
		))
		the_id = self.as_id()
		shortest_prefix_length = 0
		from arguments.IDWithFiletypeArgument import IDWithFiletypeArgument
		for f in listdir(files_dir):
			if IDWithFiletypeArgument.fits(f):
				other_id = f.split(".")[0]
				if the_id != other_id:
					prefix_overlap = 0
					while other_id[prefix_overlap] == the_id[prefix_overlap]:
						prefix_overlap += 1
					if prefix_overlap >= shortest_prefix_length:
						shortest_prefix_length = prefix_overlap + 1

		return the_id[:shortest_prefix_length]