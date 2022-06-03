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
	for weight, keys
		in INVERSE_INDEX_SOURCE_WEIGHTS.items()
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
LIBREOFFICE_CMD = '/usr/bin/libreoffice'
MAX_EXIFTOOL_ATTEMPTS = 10
EXIFTOOL_CMD = "/usr/bin/exiftool"

PDFINFO_CMD = "/usr/bin/pdfinfo"
DETEX_CMD = '/usr/bin/detex'

# For the below types, you can use the hash of the file
# as an ID.
TYPICALLY_WRITE_ONCE_FILETYPES = {
	"3GP", "AAC", "AC3", "AVI", "CD", "GIF",
	"JPEG", "JPG", "M4V", "MID", "MIDI", "MKV",
	"MOV", "MP3", "MP4", "MPEG", "MPG", "OGG",
	"PNG", "TIFF", "WAV",
} 

ROFI_ARGS = (
	'-theme'
	'Arc-Dark'
	'-theme-str'
	'"#listview{scrollbar:false;}"'
	'-fullscreen'
	'-font'
	'"Liberation Mono 18"'
)

BLACK = "\033[0;30m"
RED = "\033[0;31m"
GREEN = "\033[0;32m"
BROWN = "\033[0;33m"
BLUE = "\033[0;34m"
PURPLE = "\033[0;35m"
CYAN = "\033[0;36m"
LIGHT_GRAY = "\033[0;37m"
DARK_GRAY = "\033[1;30m"
LIGHT_RED = "\033[1;31m"
LIGHT_GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
LIGHT_BLUE = "\033[1;34m"
LIGHT_PURPLE = "\033[1;35m"
LIGHT_CYAN = "\033[1;36m"
WHITE = "\033[1;37m"
BOLD = "\033[1m"
FAINT = "\033[2m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"
BLINK = "\033[5m"
NEGATIVE = "\033[7m"
CROSSED = "\033[9m"
END = "\033[0m"

RECENT_FILE_SEARCH_MAX_ITEMS = 130