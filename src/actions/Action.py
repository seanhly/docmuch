import sys
from typing import Dict, List, Set, Optional, Type, Tuple
from abc import ABC, abstractclassmethod, abstractmethod

from arguments.Argument import Argument
from arguments.FileLikeArgument import FileLikeArgument


class Action(ABC):
	_cached_indexed_obligatory_option_groups: Optional[Dict[str, Set[str]]]
	_cached_indexed_blocking_options: Optional[Dict[str, Set[str]]]

	disqualified_options: Dict[str, str]
	conflicting_options: Dict[str, Set[str]]
	unrecognised_options: Set[str]
	missing_argument_for_options: List[str]
	incorrect_argument_type_for_options: List[Tuple[str, Argument]]
	query_parts: List[str]

	options: Dict[str, Optional[Argument]]
	file_arguments: List[FileLikeArgument]
	query: Optional[str]

	def __init__(self, arguments: Optional[List[Argument]] = None) -> None:
		self._cached_indexed_obligatory_option_groups = None
		self._cached_indexed_blocking_options = None
		self.missing_argument_for_options = []
		self.incorrect_argument_type_for_options = []
		self.disqualified_options = {}
		self.conflicting_options = {}
		self.unrecognised_options = set()
		self.options = {}
		self.query_parts = []
		self.file_arguments = []
		self.query = None
		if arguments:
			i = 0
			while i < len(arguments):
				a = arguments[i]
				i = a.parse_argument_for_action(arguments, i, self)
			self.query = " ".join(self.query_parts) if self.query_parts else None
			errors: List[str] = []
			for option in self.unrecognised_options:
				errors.append(f"unrecognised option: --{option}")
			for missing in sorted(
				set(
					[
						tuple(sorted(block + {option}))
						for option, block in self.indexed_obligatory_option_groups().items()
					]
				)
			):
				delimited_option_keys = ", ".join([f"--{o}" for o in missing])
				errors.append("one option needed from: {" + delimited_option_keys + "}")
			for conflicting in sorted(
				set(
					[
						tuple(sorted(block + {option}))
						for option, block in self.conflicting_options.items()
					]
				)
			):
				delimited_option_keys = ", ".join([f"--{o}" for o in conflicting])
				errors.append("only one option allowed from: {" + delimited_option_keys + "}")
			if errors:
				sys.stderr.write(f"Argument errors for sub-command: {self.command()}\n")
				for error in errors:
					sys.stderr.write(f"\t{error}\n")
				sys.exit(1)

	@abstractclassmethod
	def command(cls) -> str:
		pass

	@classmethod
	def name(cls) -> str:
		first_part, *the_rest = cls.command().split("-")
		return " ".join((first_part.title(), *the_rest))

	@abstractclassmethod
	def description(cls) -> str:
		pass


	def indexed_obligatory_option_groups(self) -> Dict[str, Set[str]]:
		if self._cached_indexed_obligatory_option_groups is None:
			self._cached_indexed_obligatory_option_groups = {
				o: set(g) - {o}
				for g in self.obligatory_option_groups()
				for o in g
			}
		return self._cached_indexed_obligatory_option_groups

	def indexed_blocking_options(self) -> Dict[str, Set[str]]:
		if self._cached_indexed_blocking_options is None:
			self._cached_indexed_blocking_options = {
				o: set(g) - {o}
				for g in self.blocking_options()
				for o in g
			}
		return self._cached_indexed_blocking_options

	# Specify a list of valid options.
	@abstractmethod
	def recognised_options(self) -> Set[str]:
		return set()

	# One option from each set must appear in the option list.  Each str
	# must also appear in the options field.
	@abstractmethod
	def obligatory_option_groups(self) -> List[Set[str]]:
		return []

	# Specify the blocking options, i.e.  those options that cannot appear
	# together.  As expected, each str must also appear in the options field.
	@abstractmethod
	def blocking_options(self) -> List[Set[str]]:
		return []


	# Specify the options which take an argument.
	@abstractmethod
	def arg_options(self) -> Dict[str, Type[Argument]]:
		return {}
	
	# Specific code for each action is placed within this method.
	@abstractmethod
	def execute(self) -> None:
		pass

	@classmethod
	def to_string(cls) -> str:
		return f"{cls.name()} ({cls.description()})"

	@classmethod
	def for_name(cls, name: str) -> Type["Action"]:
		from actions.Annotate import Annotate
		from actions.CopyAuthors import CopyAuthors
		from actions.CopyID import CopyID
		from actions.CopyTitle import CopyTitle
		from actions.Debug import Debug
		from actions.Delete import Delete
		from actions.EditNote import EditNote
		from actions.Index import Index
		from actions.Open import Open
		from actions.Parse import Parse
		from actions.Print import Print
		from actions.Search import Search
		from actions.Tag import Tag
		from actions.Untag import Untag
		from actions.Which import Which
		actions: List["Action"] = [
			Annotate,
			CopyAuthors,
			CopyID,
			CopyTitle,
			Debug,
			Delete,
			EditNote,
			Index,
			Open,
			Parse,
			Print,
			Search,
			Tag,
			Untag,
			Which,
		]
		for a in actions:
			if a.name() == name:
				return a