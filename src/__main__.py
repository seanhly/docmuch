#!/usr/bin/python3
import sys
from urllib import request as request
from actions.to_html import to_html
from constants import DB_PATH
from actions.extract_metadata import extract_metadata
from OutputMode import OutputMode
from actions.index import index
from actions.delete import delete
from actions.search import search
from actions.debug import debug
from actions.tag import tag
from Action import Action


action = sys.argv[1]
args = sys.argv[2:]
if action == "debug":
	debug(*args)
elif action == "tag":
	t, *args = args
	tag(t, " ".join(args))
elif action == "search":
	html = args[0] == "--html"
	is_json = args[0] == "--json"
	ids = args[0] == "--ids"
	if html:
		search_args = args[1:]
		output_mode = OutputMode.HTML
	elif ids:
		search_args = args[1:]
		output_mode = OutputMode.IDS
	elif is_json:
		search_args = args[1:]
		output_mode = OutputMode.JSON
	else:
		search_args = args
		output_mode = OutputMode.TERMINAL
	print(search(" ".join(search_args), output_mode))
elif action == "index":
	index(*args)
elif action == "delete":
	delete(*args)
elif action == "extract-metadata":
	extract_metadata(*args)
elif action == "to-html":
	to_html(*args)

#if len(args) <= 2:
#	raise ValueError("insufficient arguments")
"""
Action(
	cmd="to-html",
	min_args=1,
	fn=to_html,
)
Action(
	cmd="extract-metadata",
	min_args=0,
	fn=extract_metadata,
)
Action(
	cmd="index",
	min_args=0,
	fn=index,
)
Action(
	cmd="debug",
	min_args=0,
	fn=debug,
)
Action(
	cmd="search",
	min_args=0,
	fn=index,
	plain_args=[
		("html", "json", "ids"),
	]
)
"""