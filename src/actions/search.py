from datetime import datetime
from os.path import join, exists
from os import environ
from OutputMode import OutputMode
from constants import (
	DB_PATH,
	FILE_ANNOTATIONS_PATH,
	ID_OUTPUT_MODES,
	SEARCH_LOG_PATH,
	WINDOW_LENGTH,
)
from third_party_modules import xapian
from urllib import request as request
from JSON import JSON
import re
import sys


def search(query_string, output_mode = OutputMode.TERMINAL):
	db = xapian.Database(DB_PATH)
	timestamp = datetime.now().timestamp()
	with open(SEARCH_LOG_PATH, "a") as f:
		f.write(f"{timestamp}\t{query_string}\n")
	query_string = query_string.replace("#", "tag:")
	query_parser = xapian.QueryParser()
	query_parser.set_default_op(xapian.Query.OP_AND)
	query_parser.set_stemmer(xapian.Stem("en"))
	query_parser.set_stemming_strategy(query_parser.STEM_SOME)
	with open(f"{environ['HOME']}/.config/docmuch.json", "r") as f:
		for source in JSON.load(f)["index-sources"].keys():
			query_parser.add_prefix(source, source)
	the_query = f"{query_string}"
	try:
		query = query_parser.parse_query(the_query)
	except xapian.QueryParserError as e:
		print(e.get_msg())
		sys.exit()
	enquire = xapian.Enquire(db)
	enquire.set_query(query)
	results = []
	page = 1
	page_length = 100
	for match in enquire.get_mset((page - 1) * page_length, page_length):
		the_data = match.document.get_data().decode('utf8')
		fields = JSON.loads(the_data)
		original_file_name = fields.get("original-path", "").split("/")[-1]
		file = fields.get("file", {}) or {}
		file_id = file.get("id", "")
		suffix = file.get("type", "")
		if suffix == original_file_name:
			suffix = ""
		suffix = suffix.upper()
		fields["weight"] = match.weight
		file_annotations_path = join(FILE_ANNOTATIONS_PATH, f"{file_id}.json")
		pdf = fields.get("pdf", {}) or {}
		book = fields.get("book", {}) or {}
		tex = fields.get("tex", {}) or {}
		tei = pdf.get("tei", {}) or {}
		music = fields.get("music", {}) or {}
		if exists(file_annotations_path):
			with open(file_annotations_path, "r") as f:
				annotations = JSON.load(f)
		else:
			annotations = {}
		bib = fields.get("bib", {}) or {}
		recipe = fields.get("recipe", {}) or {}
		tei_authors = [a["name"] for a in tei.get("authors", [])]
		if len(tei_authors) == 1:
			tei_author = tei_authors[0]
		elif len(tei_authors) > 1:
			tei_author = tei_authors[0] + " et. al."
		else:
			tei_author = None
		title = tuple(
			f
			for f in (
				annotations.get("title"),
				tei.get("title"),
				pdf.get("title"),
				file.get("title"),
				book.get("title"),
				bib.get("title"),
				recipe.get("title"),
				tex.get("title"),
				music.get("title"),
				book.get("updated-title"),
				file.get("description"),
				file.get("meta-content"),
				file.get("subject"),
				book.get("description"),
				fields.get("original-path"),
			)
			if f
		)[0]
		authors = [
			f
			for f in (
				annotations.get("creators"),
				tei_author,
				bib.get("author"),
				file.get("creator-file-as"),
				file.get("creator"),
				file.get("creator-file-as"),
				pdf.get("author"),
				book.get("author"),
				tex.get("author"),
				music.get("artist"),
			)
			if f
		]
		if authors:
			for i in range(len(authors)):
				if type(authors[i]) == list:
					authors[i] = authors[i][0]
				split_authors = re.split(" and ", authors[i])
				if len(split_authors) > 1 and len(split_authors[0]) < 20:
					authors[i] = f"{split_authors[0]} et al."
				else:
					split_authors = re.split(" *[,;] *", authors[i])
					if len(split_authors) > 1 and len(split_authors[0]) > 5:
						authors[i] = f"{split_authors[0]} et al."
		id = file['id']
		if output_mode == OutputMode.HTML:
			title = re.sub("\&", "&amp;", title)
			if authors:
				before = '<span color="yellow"><i>'
				mid = f"[{authors[0].strip()}]"
				max_title_length = WINDOW_LENGTH - len(mid) - 2
				if len(title) > max_title_length:
					title = f"{title[:max_title_length]}…"
				after = "</i></span>"
				frame = f"{before}{mid}{after}".rjust(WINDOW_LENGTH + len(before) + len(after))
				result = f"<b>{title}</b>{frame[len(title):]}"
			else:
				result = f"<b>{title}</b>"
			result += f"\rid:{id}"
		elif output_mode == OutputMode.JSON:
			result = fields
		elif output_mode == OutputMode.TERMINAL:
			result = title
			if authors:
				result += f" [{authors[0]}]"
			result += f"\n\t{id}"
		elif output_mode in ID_OUTPUT_MODES:
			result = f"{id}"
		results.append(result)
	if output_mode == OutputMode.JSON:
		return JSON.dumps(results)
	elif output_mode == OutputMode.ID_LIST:
		return results
	else:
		return "\n".join(results)
