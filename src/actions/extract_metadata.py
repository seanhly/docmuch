from os import listdir
from os.path import join, basename, exists
from typing import Any, Dict, Tuple, Type
from file_types.BIB import BIB
from file_types.EBook import EBook
from file_types.Image import Image
from file_types.ODT import ODT
from file_types.PDF import PDF
from file_types.Plaintext import Plaintext
from file_types.Recipe import Recipe
from file_types.Song import Song
from file_types.TEX import TEX
from get_metadata import get_metadata
from constants import (
	FILES_PATH, FILE_INFO_PATH, MAX_SIMULTANEOUS_EXIFTOOL_REQUESTS,
	MAX_EXIFTOOL_ATTEMPTS
)
from file_types.FileType import FileType
from urllib import request as request
from JSON import JSON
from sys import stderr

SUPPORTED_FILE_TYPES: Tuple[Type[FileType]] = (
	BIB,
	EBook,
	Image,
	ODT,
	PDF,
	Plaintext,
	Recipe,
	Song,
	TEX,
)
TEXTUAL_FILE_TYPES: Tuple[Type[FileType]] = (
	EBook,
	ODT,
	PDF,
	Plaintext,
	TEX,
)


def extract_metadata(file = None):
	# If the file is None, extract metadata for all files.
	if file:
		files = [file]
	else:
		files = [join(FILES_PATH, f) for f in listdir(FILES_PATH)]
	# Make a list of the file info paths corresponding to the argument files.
	file_info_paths = {
		path: join(
			FILE_INFO_PATH,
			f"{basename(path).split('.', 1)[0]}.json",
		)
		for path in files
	}
	# The pre-existing metadata for each file.
	file_infos: Dict[
		str, # The Path
		Dict[
			str, # The file type key (e.g. book, song, etc.)
			Dict[
				str,
				Any
			]
		]
	] = {
		path: JSON.load(open(file_info_path, "r"))
		for path, file_info_path in file_info_paths.items()
		if exists(file_info_path)
	}
	# Add empty metadata placeholders where files don't already have metadata.
	file_infos.update({
		path: {}
		for path in files
		if path not in file_infos
	})
	# Create a set to track which file metadata have been changed.
	modified = set()
	# Enhance the metadata for each file, adding custom data from external
	# annotation programs.
	for path, file_info in file_infos.items():
		print(path)
		suffix = basename(path).split('.', 1)[1].upper()
		# Which file types does this file categorise under?
		supported_file_types = [
			t
			for t in SUPPORTED_FILE_TYPES
			if suffix in t.suffixes()
		]
		for t in supported_file_types:
			# Move TEI information under PDF key.
			# TODO: THIS BLOCK WILL LATER BE DELETED.
			if "tei" in file_info:
				pdf_info = file_info.get("pdf")
				if pdf_info and not pdf_info.get("tei"):
					file_info["pdf"]["tei"] = file_info["tei"]
			# Remove deprecated keys for the file type.
			# TODO: THIS BLOCK WILL LATER BE DELETED.
			for nk in t.non_keys():
				if nk in file_info:
					del file_info[nk]
					modified.add(path)
			# If the metadata is missing the filetype's key,
			# or any of the required fields within that key's
			# value (a dictionary), then we resort to the heavier
			# process of calling `t.get_info(path)`.  This often
			# involves heavier file processing.
			if (
				not file_info.get(t.key())
				or not t.required_fields().issubset(file_info[t.key()].keys())
			):
				file_info[t.key()] = t.get_info(path)
				modified.add(path)
	head_files = []
	tail_files = files
	while tail_files:
		head_files = tail_files[:MAX_SIMULTANEOUS_EXIFTOOL_REQUESTS]
		tail_files = tail_files[MAX_SIMULTANEOUS_EXIFTOOL_REQUESTS:]
		# Which files are missing EXIF data?
		missing_exif_info_for_files = {
			file
			for file in head_files
			for t in (FileType, *SUPPORTED_FILE_TYPES)
			if (
				t.key() not in file_infos[file]
				or not t.required_info_keys().issubset(file_infos[file].get(t.key()) or {})
			)
		}
		# Get the missing EXIF data.
		for attempt in range(MAX_EXIFTOOL_ATTEMPTS):
			try:
				results = get_metadata(missing_exif_info_for_files)
				break
			except Exception as e:
				stderr.write(f"{str(e)}")
				stderr.write(" ".join(missing_exif_info_for_files) + "\n")
				stderr.write(f"exiftool failure on attempt {attempt}\n")
		for result in results:
			file = result["SourceFile"]
			suffix = basename(file).split('.', 1)[1].upper()
			for t in (FileType, *SUPPORTED_FILE_TYPES):
				if t.applies_to_suffix(suffix):
					for nk in t.non_keys():
						if nk in file_infos[file]:
							del file_infos[file][nk]
							modified.add(file)
					to_update = file_infos[file].get(t.key())
					info = {
						dst: result[src]
						for src, dst in t.required_exif_mappings().items()
						if src in result
					}
					if to_update:
						for key, value in info.items():
							if value and JSON.dumps(value) != JSON.dumps(to_update.get(key)):
								to_update[key] = value
								modified.add(file)
					else:
						file_infos[file][t.key()] = info
						modified.add(file)
	for path, file_info in file_infos.items():
		file_id, suffix = basename(path).split(".", 1)
		suffix = suffix.upper()
		for t in TEXTUAL_FILE_TYPES:
			k = t.key()
			if suffix in t.suffixes():
				if k not in file_info:
					file_info[k] = dict(text=t.to_text(path))
					modified.add(path)
				elif "text" not in file_info[k]:
					file_info[k]["text"] = t.to_text(path)
					modified.add(path)
	for path, file_info in file_infos.items():
		if path in modified:
			file_info_path = join(FILE_INFO_PATH, f"{file_id}.json")
			file_content = JSON.dumps(file_info)
			with open(file_info_path, "w") as f:
				f.write(file_content)
