from os.path import join
from urllib import request as request
from os import listdir, mkdir
import subprocess
from shutil import rmtree
from file_types.FileType import FileType
from sys import stderr
from constants import MAX_LIBREOFFICE_ATTEMPTS, LIBREOFFICE_CMD


class ODT(FileType):
	@classmethod
	def to_text(cls, fa):
		for attempt in range(MAX_LIBREOFFICE_ATTEMPTS):
			try:
				the_dir = "/tmp/docmuch_odt/"
				mkdir(the_dir)
				subprocess.check_output(
					[
						LIBREOFFICE_CMD,
						"--convert-to",
						"txt",
						"--outdir",
						the_dir,
						fa.as_full_typed_file_path(cls)
					],
					stderr=subprocess.DEVNULL
				)
				for f in listdir(the_dir):
					with open(join(the_dir, f)) as f:
						content = f.read().strip()
				rmtree(the_dir)
			except Exception:
				rmtree(the_dir)
				stderr.write(f"exiftool failure on attempt {attempt}\n")
		return content

	@classmethod
	def key(cls):
		return "odt"

	@classmethod
	def required_exif_mappings(cls):
		return {}

	@classmethod
	def required_fields(cls):
		return set()

	@classmethod
	def suffixes(cls):
		return {"ODT"}