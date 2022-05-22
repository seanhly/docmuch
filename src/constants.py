from os import environ, makedirs
from os.path import join, exists
from OutputMode import OutputMode
from typing import Tuple, List
from urllib import request as request

WINDOW_LENGTH = 130
DOCUMENTS_PATH = join(environ['HOME'], "Documents")
DB_PATH = join(DOCUMENTS_PATH, "Index")
FILES_PATH = join(DOCUMENTS_PATH, "Files")
FILE_INFO_PATH = join(DOCUMENTS_PATH, "FileInfo")
FILE_ANNOTATIONS_PATH = join(DOCUMENTS_PATH, "FileAnnotations")
SEARCH_LOG_PATH = join(DOCUMENTS_PATH, "search_log.tsv")
for f in (DB_PATH, FILES_PATH, FILE_INFO_PATH):
	if not exists(f):
		makedirs(f)
ID_OUTPUT_MODES = set([OutputMode.IDS, OutputMode.ID_LIST])
INVERSE_INDEX_SOURCE_WEIGHTS: List[Tuple[str, int]] = {
	256: [
		"original_path",
	],
	128: [
		"title",
	],
	64: [
		"author",
	],
	48: [
		"album",
		"filetype",
		"genre",
	],
	32: [
		"description",
	],
	16: [
		"text",
	],
	1: [
		"ingredients",
		"method",
		"date",
		"organisation",
		"language",
		"id",
		"pages",
		"size",
		"duration",
		"serves",
		"tag",
		"track",
		"disc",
		"width",
		"height",
	]
}
INDEX_SOURCE_WEIGHTS = {
	key: weight
	for weight, keys in INVERSE_INDEX_SOURCE_WEIGHTS.items()
	for key in keys
}
DISCARD_KEY_PATHS_PRE_DATA_STORE = [
	("pdf", "tei", "body"),
	("pdf", "text"),
	("file", "text"),
	("book", "text"),
]
MAX_SIMULTANEOUS_EXIFTOOL_REQUESTS = 100
MAX_LIBREOFFICE_ATTEMPTS = 10
MAX_EXIFTOOL_ATTEMPTS = 10