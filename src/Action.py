from typing import List, Tuple, NamedTuple, Callable


class Action(NamedTuple):
	cmd: str
	min_args: int
	plain_args: List[
		# Each of these tuples are blocking groups, i.e. only one arg per
		# group/tuple may appear on the CLI.
        Tuple[str]
    ]
	valued_args: List[
		Tuple[str]
	]
	fn: Callable