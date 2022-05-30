#!/usr/bin/python3
import sys
from urllib import request as request
from actions.to_html import to_html
from actions.Parse import Parse
from actions.Index import Index
from actions.Delete import Delete
from actions.Search import Search
from actions.Debug import Debug
from actions.Open import Open
from actions.Which import Which
from actions.Tag import Tag
from parse_dynamic_argument import parse_dynamic_argument


action = sys.argv[1]
args = sys.argv[2:]
arguments = [
	parse_dynamic_argument(arg, action)
	for arg in args
]
if action == Debug.command():
	Debug(arguments).execute()
elif action == Search.command():
	Search(arguments).execute()
elif action == Index.command():
	Index(arguments).execute()
elif action == Parse.command():
	Parse(arguments).execute()
elif action == Parse.command():
	Delete(arguments).exeute()
elif action == Open.command():
	Open(arguments).execute()
elif action == Which.command():
	Which(arguments).execute()
elif action == Tag.command():
	Tag(arguments).execute()
sys.exit(0)
if False:
	pass
elif action == "to-html":
	to_html(arguments)

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