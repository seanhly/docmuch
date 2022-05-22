from OutputMode import OutputMode
from actions.search import search
from actions.tag_file_id import tag_file_id
from urllib import request as request
import re

def tag(the_tag, query_or_file_id):
	actual_tag = the_tag[1:]
	remove = the_tag[0] == "-"
	if re.fullmatch("[0-9a-f]{40}", query_or_file_id):
		modified = tag_file_id(actual_tag, query_or_file_id, remove)
		if modified:
			print(f"{the_tag}\t{query_or_file_id}")
	else:
		for file_id in search(
			query_or_file_id,
			OutputMode.ID_LIST,
		):
			modified = tag_file_id(actual_tag, file_id, remove)
			if modified:
				print(f"{the_tag}\t{file_id}")

