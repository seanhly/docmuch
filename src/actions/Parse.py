from os import environ, listdir
from os.path import join
from JSON import JSON
from actions.Action import Action
from arguments.FileLikeArgument import FileLikeArgument
from arguments.IDArgument import IDArgument
from arguments.PathArgument import PathArgument
from file_types.BIB import BIB
from file_types.EBook import EBook
from file_types.FileType import FileType
from file_types.Image import Image
from file_types.ODT import ODT
from file_types.PDF import PDF
from file_types.Plaintext import Plaintext
from file_types.Recipe import Recipe
from file_types.Song import Song
from file_types.TEX import TEX
from os.path import exists
from sys import stderr
from typing import Any, Dict, Tuple, Type, List, Set
from typing import Dict
from urllib import request as request
import subprocess
from constants import (
	MAX_SIMULTANEOUS_EXIFTOOL_REQUESTS,
	MAX_EXIFTOOL_ATTEMPTS, EXIFTOOL_CMD,
)

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


def get_metadata(paths: Set[str]):
	if paths:
		metadata = JSON.loads(subprocess.check_output(
			[EXIFTOOL_CMD, "-G", "-j", "-n", *paths],
			stderr=subprocess.DEVNULL
		))
	else:
		metadata = []
	return metadata


class Parse(Action):
	@classmethod
	def command(cls) -> str:
		return "parse"

	@classmethod
	def description(cls):
		return "parse the file for associated metadata"

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
		previous_metadata: List[FileLikeArgument] = []
		no_metadata: List[FileLikeArgument] = []
		for fa in self.file_arguments:
			print(str(fa.as_id()))
			(
				previous_metadata
				if exists(fa.as_full_metadata_path())
				else no_metadata
			).append(fa)
		# The pre-existing metadata for each file.
		file_infos: Dict[
			str, # The file ID
			Tuple[
				FileLikeArgument, # The file
				Dict[
					str, # The file type key (e.g. book, song, etc.)
					Dict[
						str,
						Any
					]
				]
			]
		] = {
			fa.as_id(): (fa, JSON.load(open(fa.as_full_metadata_path(), "r")))
			for fa in previous_metadata
		}
		file_infos.update({
			fa.as_id(): (fa, {})
			for fa in no_metadata
		})
		# Create a set to track which file metadata have been changed.
		modified: Set[str] = set()
		# Enhance the metadata for each file, adding custom data from external
		# annotation programs.
		for file_id, (fa, file_info) in file_infos.items():
			# Which file types does this file categorise under?
			for t in SUPPORTED_FILE_TYPES:
				if t.applies_to_fa(fa):
					# Move TEI information under PDF key.
					# TODO: THIS BLOCK WILL LATER BE DELETED.
					if "tei" in file_info:
						pdf_info = file_info.get("pdf")
						if pdf_info and not pdf_info.get("tei"):
							file_info["pdf"]["tei"] = file_info["tei"]
							modified.add(file_id)
					# Remove deprecated keys for the file type.
					# TODO: THIS BLOCK WILL LATER BE DELETED.
					for nk in t.non_keys():
						if nk in file_info:
							del file_info[nk]
							modified.add(file_id)
					# If the metadata is missing the filetype's key,
					# or any of the required fields within that key's
					# value (a dictionary), then we resort to the heavier
					# process of calling `t.get_info(path)`.  This often
					# involves heavier file processing.
					if (
						not file_info.get(t.key())
						or not t.required_fields().issubset(file_info[t.key()].keys())
					):
						# --- HEAVY PROCESSING FROM EXTERNAL PROGRAM HAPPENS BELOW ---
						file_info[t.key()] = t.get_info(fa)
						modified.add(file_id)
		head_files: List[FileLikeArgument] = []
		tail_files: List[FileLikeArgument] = self.file_arguments
		while tail_files:
			head_files = tail_files[:MAX_SIMULTANEOUS_EXIFTOOL_REQUESTS]
			tail_files = tail_files[MAX_SIMULTANEOUS_EXIFTOOL_REQUESTS:]
			# Which files are missing EXIF data?
			missing_exif_info_for_files = {
				path
				for fa in head_files
				for path in fa.as_full_file_paths()
				for t in (FileType, *SUPPORTED_FILE_TYPES)
				if (
					t.applies_to_any_suffix(PathArgument(path).as_filetypes())
					and (
						t.key() not in file_infos[fa.as_id()][1]
						or not t.required_info_keys().issubset(
							file_infos[fa.as_id()][1].get(t.key())
							or {}
						)
					)
				)
			}
			# Get the missing EXIF data.
			for attempt in range(MAX_EXIFTOOL_ATTEMPTS):
				try:
					results = get_metadata(missing_exif_info_for_files)
					break
				except Exception as e:
					stderr.write(f"{str(e)}")
					stderr.write(" ".join([
						path
						for fa in missing_exif_info_for_files
						for path in fa.as_full_file_paths()
					]) + "\n")
					stderr.write(f"exiftool failure on attempt {attempt}\n")
			for result in results:
				fa = PathArgument(result["SourceFile"])
				print(str(fa))
				for t in (FileType, *SUPPORTED_FILE_TYPES):
					if t.applies_to_any_suffix(fa.as_filetypes()):
						for nk in t.non_keys():
							if nk in file_infos[fa.as_id()][1]:
								del file_infos[fa.as_id()][1][nk]
								modified.add(fa.as_id())
						to_update = file_infos[fa.as_id()][1].get(t.key())
						info = {
							dst: result[src]
							for src, dst in t.required_exif_mappings().items()
							if src in result
						}
						if to_update:
							for key, value in info.items():
								if value and (
									JSON.dumps(value) != JSON.dumps(to_update.get(key))
								):
									to_update[key] = value
									modified.add(fa.as_id())
						else:
							file_infos[fa.as_id()][1][t.key()] = info
							modified.add(fa.as_id())
		for id, (fa, file_info) in file_infos.items():
			for t in TEXTUAL_FILE_TYPES:
				k = t.key()
				if t.suffixes() and t.applies_to_any_suffix(fa.as_filetypes()):
					if k not in file_info:
						file_info[k] = dict(
							text=t.to_text(fa)
						)
						modified.add(fa.as_id())
					elif "text" not in file_info[k]:
						file_info[k]["text"] = t.to_text(fa)
						modified.add(fa.as_id)
		for id, (fa, file_info) in file_infos.items():
			if id in modified:
				with open(fa.as_full_metadata_path(), "w") as f:
					JSON.dump(file_info, f)