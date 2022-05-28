from os import unlink
from os.path import exists
from file_types.FileType import FileType
from typing import Set
from urllib import request as request
import subprocess

class EBook(FileType):
	@classmethod
	def to_text(cls, fa):
		CMD = '/usr/bin/ebook-convert'
		if not exists(CMD):
			raise RuntimeError('System command not found: %s' % CMD)
		tmp_txt_file = "/tmp/ebook.txt"
		subprocess.check_output(
			[CMD, fa.as_full_typed_file_path(cls), tmp_txt_file],
			stderr=subprocess.DEVNULL
		)
		with open(tmp_txt_file, "r") as f:
			txt_content = f.read().strip()
		unlink(tmp_txt_file)
		return txt_content

	@classmethod
	def key(cls):
		return "book"

	@classmethod
	def non_keys(cls):
		return {
			"image",
			"music",
			"tei",
		}

	@classmethod
	def suffixes(cls) -> Set[str]:
		return set(["MOBI", "EPUB", "DJVU"])

	@classmethod
	def required_exif_mappings(cls):
		return {
			"Palm:BookName": "title",
			"XMP:Title": "title",
			"Palm:UpdatedTitle": "updated-title",
			"Palm:Description": "description",
			"XMP:Description": "description",
			"Palm:Author": "author",
			"XMP:Creator": "author",
			"Palm:Publisher": "publisher",
			"XMP:Publisher": "publisher",
			"Palm:Language": "language",
			"Palm:Subject": "subject",
			"XMP:Subject": "subject",
			"Palm:ISBN": "isbn",
			"Palm:PublishDate": "published",
			"XMP:Rights": "rights",
			"XMP:Keywords": "keywords",
			"XMP:CreatorFile-as": "creator-file-as",
			"XMP:MetaContent": "meta-content",
			"XMP:Date": "published",
			"XMP:Language": "language",
		}

	@classmethod
	def required_fields(cls):
		return set()