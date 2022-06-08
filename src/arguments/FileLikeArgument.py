from abc import abstractmethod
from os import listdir
from typing import Set, Type, Set
from arguments.Argument import Argument
from os.path import basename, join
import re
from file_types.FileType import FileType
from constants import (
	FILE_INFO_PATH,
	FILE_ANNOTATIONS_PATH,
	FILE_NOTES_PATH,
	FILES_PATH
)


VALID_FILE_NAME = "[0-9a-f]{40}" + FileType.valid_suffix_pattern()


id_trie = {}


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
		return join(FILE_INFO_PATH, f"{self.as_id()}.json")
	
	def as_full_annotations_path(self):
		return join(FILE_ANNOTATIONS_PATH, f"{self.as_id()}.json")
	
	def as_full_file_note_path(self):
		return join(FILE_NOTES_PATH, f"{self.as_id()}.MD")

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
		the_id = self.as_id()
		shortest_prefix_length = 0
		global id_trie
		if not id_trie:
			j = 0
			directory_files = listdir(FILES_PATH)
			file_ids = {
				f.split(".")[0]
				for f in directory_files
				if re.match(VALID_FILE_NAME, f)
			}
			for file_id in file_ids:
				j += 1
				i = 0
				trie = id_trie
				inserted = False
				while not inserted:
					if file_id[i] in trie:
						leaf = trie[file_id[i]]
						if type(leaf) == str:
							next_trie = {}
							trie[file_id[i]] = next_trie
							j = i
							while leaf[i - j] == file_id[i + 1]:
								d = {}
								next_trie[file_id[i + 1]] = d
								next_trie = d
								i += 1
							next_trie[leaf[i - j]] = leaf[i - j + 1:]
							next_trie[file_id[i + 1]] = file_id[i + 2:]
							inserted = True
						else:
							trie = leaf
							i += 1
					else:
						trie[file_id[i]] = file_id[i + 1:]
						inserted = True
		trie = id_trie
		shortest_prefix_length = 0
		the_id = self.as_id()
		while type(trie) != str:
			trie = trie[the_id[shortest_prefix_length]]
			shortest_prefix_length += 1

		return the_id[:shortest_prefix_length]
