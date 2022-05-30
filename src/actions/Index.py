from os import environ, listdir
from os.path import exists, join
from constants import (
	DB_PATH,
	DISCARD_KEY_PATHS_PRE_DATA_STORE,
	INDEX_SOURCE_WEIGHTS
)
from arguments.IDArgument import IDArgument
from third_party_modules import xapian
from urllib import request as request
from JSON import JSON
from typing import Dict, List
from PreIndexFunctions import PreIndexFunctions
from actions.Action import Action


class Index(Action):
	@classmethod
	def command(cls) -> str:
		return "index"

	@classmethod
	def description(cls):
		return "index the file"

	def recognised_options(self):
		return {"all"}

	def arg_options(self):
		return set()

	def obligatory_option_groups(self):
		return []

	def blocking_options(self):
		return []
	
	def execute(self) -> None:
		if "all" in self.options:
			self.file_arguments = [
				IDArgument(f.split(".", 1)[0])
				for f in listdir(join(environ['HOME'], "Documents", "Files"))
			]
		index_source_metadata: Dict[str, List[List[str]]] = {}
		with open(join(environ['HOME'], ".config", "docmuch.json"), "r") as f:
			index_source_metadata = JSON.load(f)["index-sources"]
		db = xapian.WritableDatabase(DB_PATH, xapian.DB_CREATE_OR_OPEN)
		term_generator = xapian.TermGenerator()
		term_generator.set_stemmer(xapian.Stem("en"))
		for fa in self.file_arguments:
			file_info_path = fa.as_full_metadata_path()
			file_annotations_path = fa.as_full_annotations_path()
			with open(file_info_path, "r") as f:
				info = JSON.load(f)
			if exists(file_annotations_path):
				with open(file_annotations_path, "r") as f:
					info["annotations"] = JSON.load(f)
			info["file"]["id"] = fa.as_id()
			info["file"]["type"] = sorted(fa.as_filetypes())
			index_source_data: Dict[str, List[str]] = {}
			for key, paths in index_source_metadata.items():
				for path in paths:
					index_part = info
					for path_part in path:
						if path_part[0] == "@":
							index_part = PreIndexFunctions.__dict__[path_part[1:]](index_part)
						else:
							index_part = index_part.get(path_part)
							if not index_part:
								break
					if index_part:
						if key in index_source_data:
							if type(index_part) == list:
								index_source_data[key] += index_part
							else:
								index_source_data[key].append(index_part)
						else:
							if type(index_part) == list:
								index_source_data[key] = index_part
							else:
								index_source_data[key] = [index_part]
			doc = xapian.Document()
			term_generator.set_document(doc)
			for label, content in index_source_data.items():
				weight = INDEX_SOURCE_WEIGHTS[label]
				if type(content) == list:
					for item in content:
						term_generator.index_text(str(item), weight, label)
						term_generator.increase_termpos()
				else:
					term_generator.index_text(str(content), weight, label)
			for label, content in index_source_data.items():
				weight = INDEX_SOURCE_WEIGHTS[label]
				if type(content) == list:
					for row in content:
						term_generator.increase_termpos()
						term_generator.index_text(str(row), weight)
				else:
					term_generator.increase_termpos()
					term_generator.index_text(str(content), weight)
			for path in DISCARD_KEY_PATHS_PRE_DATA_STORE:
				*path, key = path
				sub_info = info
				for part in path:
					sub_info = info.get(part)
					if not sub_info:
						break
				if sub_info and key in sub_info:
					del sub_info[key]
			doc.set_data(fa.as_id())
			doc.add_boolean_term(fa.as_id())
			db.replace_document(fa.as_id(), doc)
