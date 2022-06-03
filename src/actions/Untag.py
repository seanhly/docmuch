from JSON import JSON
from actions.Action import Action
from actions.Tag import Tag
from os.path import exists
from urllib import request as request


class Untag(Action):
	tag: str

	@classmethod
	def command(cls) -> str:
		return "untag"

	@classmethod
	def description(cls):
		return "remove a file's tag"

	def recognised_options(self):
		return set()

	def arg_options(self):
		return set()

	def obligatory_option_groups(self):
		return []

	def blocking_options(self):
		return []
	
	def execute(self):
		self.tag = Tag.read_tag()
		if self.file_arguments:
			for fa in self.file_arguments:
				modified = False
				file_annotations_path = fa.as_full_annotations_path()
				if exists(file_annotations_path):
					with open(file_annotations_path, "r") as f:
						file_annotations = JSON.load(f)
					tags = set(file_annotations.get("tags", []))
				else:
					file_annotations = {
						"title": None,
						"creators": None,
					}
					tags = set()
				modified = self.tag in tags
				tags.discard(self.tag)
				file_annotations["tags"] = sorted(tags)
				with open(file_annotations_path, "w") as f:
					JSON.dump(file_annotations, f)
				if modified:
					print(fa.as_id())
		else:
			raise ValueError("""
				There is not yet any code for untagging things via a search query.
			""")