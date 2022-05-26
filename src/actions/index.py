from os import listdir, environ
from os.path import join, basename, exists
from constants import (
	DB_PATH,
	DISCARD_KEY_PATHS_PRE_DATA_STORE,
	FILES_PATH,
	FILE_ANNOTATIONS_PATH,
	FILE_INFO_PATH,
	INDEX_SOURCE_WEIGHTS
)
from third_party_modules import xapian
from urllib import request as request
from JSON import JSON
from typing import Dict, List
from PreIndexFunctions import PreIndexFunctions


def index(
	file_path = None,
	db = None,
	term_generator = None
):
	index_source_metadata: Dict[str, List[List[str]]] = {}
	with open(f"{environ['HOME']}/.config/docmuch.json", "r") as f:
		index_source_metadata = JSON.load(f)["index-sources"]
	if not db:
		db = xapian.WritableDatabase(DB_PATH, xapian.DB_CREATE_OR_OPEN)
	if not term_generator:
		term_generator = xapian.TermGenerator()
		term_generator.set_stemmer(xapian.Stem("en"))
	if not file_path:
		for f in listdir(FILES_PATH):
			index(join(FILES_PATH, f), db, term_generator)
	else:
		print(file_path)
		file_name = basename(file_path)
		file_id, suffix = file_name.split(".", 1)
		suffix = suffix.upper()
		file_info_path = join(FILE_INFO_PATH, f"{file_id}.json")
		file_annotations_path = join(FILE_ANNOTATIONS_PATH, f"{file_id}.json")
		with open(file_info_path, "r") as f:
			info = JSON.load(f)
		if exists(file_annotations_path):
			with open(file_annotations_path, "r") as f:
				info["annotations"] = JSON.load(f)
		info["file"]["id"] = file_id
		info["file"]["type"] = suffix
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
		print(" ".join(index_source_data.keys()))
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
		print(info)
		doc.set_data(JSON.dumps(info))
		doc.add_boolean_term(file_id)
		db.replace_document(file_id, doc)
