#!/usr/bin/python3
import subprocess
import sys
from typing import Optional, Type
from urllib import request as request
from parse_dynamic_argument import parse_dynamic_argument
from os import environ
from actions import Action

if "TMUX" not in environ:
	# I have plans to make the script run from a TMUX session permanently (as a
	# server), in order to remove the Python startup time at the begin of each
	# commandline usage.
	tmux = subprocess.Popen(
		[
			"/usr/bin/tmux",
			"new-session",
			"-s",
			"docmuch",
			' '.join(sys.argv),
		]
	)
	tmux.wait()
else:
	action = sys.argv[1]
	args = sys.argv[2:]
	arguments = [
		parse_dynamic_argument(arg, action)
		for arg in args
	]
	FoundAction: Optional[Type[Action]] = None
	for T in Action.__subclasses__():
		if action == T.command():
			FoundAction = T
			break
	if FoundAction:
		FoundAction(arguments).execute()
		exit_code = 0
	else:
		sys.stderr.write(f"unknown sub-command: {action}\n")
		exit_code = 1
	sys.exit(exit_code)