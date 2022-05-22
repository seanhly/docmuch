from json import dump, dumps, load, loads
from typing import Any

DUMP_ARGS = dict(
	separators=(",", ": "),
	sort_keys=True,
	indent="\t",
)

class JSON:
	@classmethod
	def dumps(cls, obj: Any):
		return dumps(obj, **DUMP_ARGS)

	@classmethod
	def dump(cls, f):
		return dump(f, **DUMP_ARGS)

	@classmethod
	def loads(cls, content: str):
		return loads(content)

	@classmethod
	def load(cls, f):
		return load(f)