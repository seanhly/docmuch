from os.path import basename
from constants import DB_PATH
from third_party_modules import xapian
from urllib import request as request


def delete(
	file_path,
	db = None
):
	if not db:
		db = xapian.WritableDatabase(DB_PATH, xapian.DB_CREATE_OR_OPEN)
	print(file_path)
	file_name = basename(file_path)
	file_id = file_name.split(".", 1)[0]
	print(file_id)
	db.delete_document(file_id)
