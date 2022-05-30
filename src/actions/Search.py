from datetime import datetime
from enum import Enum
from os.path import join, exists, realpath
from os import environ
from typing import List, Set, Tuple, Type
from actions.Action import Action
from arguments.FileLikeArgument import FileLikeArgument
from arguments.IDArgument import IDArgument
from arguments.IDPrefixArgument import IDPrefixArgument
from arguments.IDWithFiletypeArgument import IDWithFiletypeArgument
from arguments.OtherArgument import OtherArgument
from constants import (
	DB_PATH,
	END,
	GREEN,
	RECENT_FILE_SEARCH_MAX_ITEMS,
	RED,
	SEARCH_LOG_PATH,
	WHITE,
	YELLOW,
)
from file_types.FileType import FileType
from third_party_modules import xapian
from urllib import request as request
from JSON import JSON
import re
import sys
import subprocess

class BreadcrumbDirection(Enum):
	BACK = -1
	REMAIN = 0
	FORWARD = 1


class Search(Action):
	@classmethod
	def command(cls) -> str:
		return "search"

	@classmethod
	def description(cls):
		return "search for files"

	def recognised_options(self):
		#return {"format"}
		return set()

	def arg_options(self):
		#return {"format": OtherArgument}
		return {}

	def obligatory_option_groups(self):
		return []

	def blocking_options(self):
		return []
	
	def initial_query(self, query, **_):
		files_dir = realpath(join(
			environ.get("HOME"),
			"Documents",
			"Files",
		))
		if not query:
			list_recently_accessed = subprocess.Popen(
				["ls", "-u", files_dir],
				stdout=subprocess.PIPE,
			)
			# This will give a little speed bump, if it so
			# happens that `ls -u` uses a lot of `stat` system
			# calls.
			prematurely_stop_listing = subprocess.Popen(
				["head", f"-{RECENT_FILE_SEARCH_MAX_ITEMS}"],
				stdin=list_recently_accessed.stdout,
				stdout=subprocess.PIPE,
			)
			while prematurely_stop_listing.returncode is None:
				prematurely_stop_listing.poll()
			files = prematurely_stop_listing.stdout.read().decode("utf8").strip().split("\n")
			matching_files_and_weights = [
				(score, IDWithFiletypeArgument(f))
				for score, f in enumerate(reversed(files), start=1)
			]
		else:
			db = xapian.Database(DB_PATH)
			timestamp = datetime.now().timestamp()
			with open(SEARCH_LOG_PATH, "a") as f:
				f.write(f"{timestamp}\t{query}\n")
			query_parser = xapian.QueryParser()
			query_parser.set_default_op(xapian.Query.OP_AND)
			query_parser.set_stemmer(xapian.Stem("en"))
			query_parser.set_stemming_strategy(query_parser.STEM_SOME)
			with open(f"{environ['HOME']}/.config/docmuch.json", "r") as f:
				for source in JSON.load(f)["index-sources"].keys():
					query_parser.add_prefix(source, source)
				try:
					query_string = query.replace("#", "tag:")
					parsed_query = query_parser.parse_query(query_string)
				except xapian.QueryParserError as e:
					print(e.get_msg())
					sys.exit()
				enquire = xapian.Enquire(db)
				enquire.set_query(parsed_query)
				page = 1
				page_length = 50
				matches = [m for m in enquire.get_mset((page - 1) * page_length, page_length)]
				matching_files_and_weights = [
					(
						match.weight,
						IDArgument(match.document.get_data().decode("utf8")),
					)
					for match in matches
				]

		return (
			query,
			dict(matching_files_and_weights=matching_files_and_weights),
		)

	def execute(self):
		query = self.query
		steps = [
			(
				self.initial_query,
				lambda q, matching_files_and_weights:
					BreadcrumbDirection.FORWARD
			),
			(
				self.select_files,
				lambda q, chosen_files: (
					BreadcrumbDirection.FORWARD
					if chosen_files
					else BreadcrumbDirection.BACK
				)
			),
			(
				self.choose_action,
				lambda q, action: (
					BreadcrumbDirection.FORWARD
					if action
					else (
						BreadcrumbDirection.REMAIN
						if q
						else BreadcrumbDirection.BACK
					)
				)
			),
			(
				self.execute_action,
				lambda _: BreadcrumbDirection.FORWARD
			)
		]
		# First function's kwargs.
		kwargs = [
			dict()
		] + [None] * (len(steps) - 1)
		queries = [
			query,
			"",
		] + [None] * (len(steps) - 2)
		# Functioning readcrumbs are good UX.
		i = 0
		while i >= 0 and i < len(steps):
			step_fn, determine_next_step = steps[i]
			if kwargs[i]:
				used_query, next_kwargs = step_fn(queries[i], **kwargs[i])
			else:
				used_query, next_kwargs = step_fn(queries[i])
			next_step = determine_next_step(used_query, **next_kwargs)
			if next_step == BreadcrumbDirection.FORWARD:
				if i == 1:
					queries[0] = used_query
					queries[1] = ""
				else:
					queries[i] = used_query
				i += 1
				if next_kwargs:
					kwargs[i] = next_kwargs
			elif next_step == BreadcrumbDirection.BACK:
				if i <= 1 and not used_query:
					sys.exit(0)
				else:
					kwargs[i] = None
					if i == 1:
						queries[0] = used_query
						queries[1] = ""
				i -= 1
			elif next_step == BreadcrumbDirection.REMAIN:
				queries[i] = ""

	def execute_action(self, query, action: Type[Action]):
		action.execute()
		return query, {}

	def select_files(self, query, matching_files_and_weights: List[Tuple[float, FileLikeArgument]]):
		display_results = []
		for weight, fa in reversed(matching_files_and_weights):
			with open(fa.as_full_metadata_path(), "r") as f:
				fields = JSON.load(f)
			file = fields.get("file", {}) or {}
			fields["weight"] = weight
			file_annotations_path = fa.as_full_annotations_path()
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
			pages = [
				p
				for p in (
					pdf.get("pages"),
				)
				if p
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
			result = f"{RED}{fa.shortest_id_prefix()}{END}\t"
			if pages:
				likely_page_count = pages[0]
				page_count_string = f"{likely_page_count}p"
				result += f"{GREEN}{page_count_string.ljust(5)}{END} "
			else:
				result += f"      "
			filetypes = " ".join(sorted(fa.as_filetypes()))
			result += f"{GREEN}{filetypes}{END} "
			if authors:
				result += f"{YELLOW}[{authors[0]}]{END} "
			result += f"{WHITE}{title}{END}"
			display_results.append(result)
		fzf_search = subprocess.Popen(
			[
				"fzf",
				"--print-query",
				"--multi",
				"--exact",
				"--no-mouse",
				"--ansi",
			],
			stdin=subprocess.PIPE,
			stdout=subprocess.PIPE,
		)
		for r in display_results:
			fzf_search.stdin.write(bytes(f"{r}\n", encoding="utf8"))
		fzf_search.stdin.close()
		while fzf_search.returncode is None:
			fzf_search.poll()
		fzf_output = fzf_search.stdout.read().decode("utf8").split("\n", 1)
		if len(fzf_output) == 2:
			potential_next_query, selected_lines_str = fzf_output
			if potential_next_query:
				query = potential_next_query
			chosen_files: List[FileLikeArgument] = []
			if selected_lines_str:
				selected_lines = selected_lines_str.strip().split("\n")
				for line in selected_lines:
					id_prefix = re.match("[0-9a-f]+", line)[0]
					fa = IDPrefixArgument(id_prefix)
					chosen_files.append(fa)
		elif len(fzf_output) == 1:
			query = fzf_output[0].strip()
			chosen_files = []
		else:
			query = None
			chosen_files = []
		
		return query, dict(chosen_files=chosen_files)

	def choose_action(
		self,
		query: str,
		chosen_files: List[FileLikeArgument],
	):
		suffixes: Set[str] = set()
		for fa in chosen_files:
			for suffix in fa.as_filetypes():
				suffixes.add(suffix)
		seen_actions: Set[Type[Action]] = set()
		available_actions_for_files: List[Type[Action]] = []
		for action_group in [
			FileType.for_suffix(suffix).actions()
			for suffix in suffixes
		]:
			for action in action_group:
				if action not in seen_actions:
					seen_actions.add(action)
					available_actions_for_files.append(action)
		fzf_search = subprocess.Popen(
			[
				"fzf",
				"--print-query",
				"--exact",
				"--no-mouse",
				f"--prompt={len(chosen_files)} file(s) selected > ",
				f"--query={query or ''}",
			],
			stdin=subprocess.PIPE,
			stdout=subprocess.PIPE,
		)
		for action in available_actions_for_files:
			fzf_search.stdin.write(
				bytes(f"{action.to_string()}\n", encoding="utf8")
			)
		fzf_search.stdin.close()
		while fzf_search.returncode is None:
			fzf_search.poll()
		fzf_output = fzf_search.stdout.read().decode("utf8").split("\n", 1)
		if len(fzf_output) == 0:
			action = None
			query = ""
		if len(fzf_output) == 1:
			action = None
			query = fzf_output[0].strip()
		else:
			query, selected_action_string = fzf_output
			if selected_action_string:
				name = selected_action_string.strip().split(" (")[0]
				ChosenAction = Action.for_name(name)
				action = ChosenAction(chosen_files)
			else:
				action = None

		return query, dict(action=action)