from abc import ABC
from os.path import basename, join, exists
from typing import Set, Dict, Any, List, Tuple
from constants import FILE_INFO_PATH, FILE_ANNOTATIONS_PATH
from JSON import JSON
import re


class FileType(ABC):
	@classmethod
	def key(cls) -> str:
		return "file"

	@classmethod
	def suffixes(cls) -> Set[str]:
		return set()

	@classmethod
	def applies_to_suffix(cls, suffix):
		suffixes = cls.suffixes()
		return not suffixes or suffix in suffixes

	@classmethod
	def get_info(cls, file) -> Dict[str, Any]:
		return {}

	@classmethod
	def to_text(cls, file) -> str:
		raise ValueError("unimplemented function: FileType.to_text(file)")

	@classmethod
	def required_exif_mappings(cls) -> Dict[str, str]:
		return {
			"File:FileSize": "size",
			"File:FileType": "type",
		}

	@classmethod
	def required_fields(cls):
		return {
			"size",
			"type",
		}

	@classmethod
	def required_info_keys(cls) -> Set[str]:
		return set(cls.required_exif_mappings().values())

	@classmethod
	def non_keys(cls) -> Set[str]:
		return {
			"tei"
		}