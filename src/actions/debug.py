from os import listdir
from os.path import join
from constants import FILES_PATH
from get_metadata import get_metadata
import json


def debug(path = None):
	if path:
		paths = [path]
	else:
		paths = [join(FILES_PATH, f) for f in listdir(FILES_PATH)]
	print(
		json.dumps(
			get_metadata(paths),
			separators=(",", ":"),
		)
	)
