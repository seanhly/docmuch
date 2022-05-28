from abc import ABC, abstractclassmethod
from typing import Set, Dict, Any


class FileType(ABC):
	@classmethod
	def key(cls) -> str:
		return "file"

	@classmethod
	def suffixes(cls) -> Set[str]:
		return set()

	@classmethod
	def applies_to_suffix(cls, suffix: str):
		return cls.applies_to_any_suffix({suffix})

	@classmethod
	def applies_to_any_suffix(cls, suffixes: Set[str]):
		return not cls.suffixes() or not suffixes.isdisjoint(cls.suffixes())


	@classmethod
	def applies_to_fa(cls, fa: "FileLikeArgument"):
		return cls.applies_to_any_suffix(fa.as_filetypes())

	@abstractclassmethod
	def get_info(cls, fa: "FileLikeArgument") -> Dict[str, Any]:
		return {}

	@classmethod
	def to_text(cls, fa: "FileLikeArgument") -> str:
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