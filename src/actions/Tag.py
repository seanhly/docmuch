from os.path import realpath, join
import subprocess
from os import environ
from JSON import JSON
from actions.Action import Action
from arguments.TagArgument import TagArgument
from os.path import exists
from urllib import request as request


class Tag(Action):
	tag: TagArgument = None

	@classmethod
	def command(cls) -> str:
		return "tag"

	@classmethod
	def description(cls):
		return "tag files"

	def recognised_options(self):
		return set()

	def arg_options(self):
		return set()

	def obligatory_option_groups(self):
		return []

	def blocking_options(self):
		return []
	
	def execute(self):
		if not self.tag:
			tags_path = realpath(join(
				environ.get("HOME"),
				"Documents",
				"tags.tsv",
			))
			with open(tags_path, "r") as f:
				tags = [l.strip().split("\t") for l in f.read().strip().split("\n")]
			self.tag = TagArgument()
			fzf_search = subprocess.Popen(
				[
					"fzf",
					"--print-query",
					"--exact",
					"--no-mouse",
				],
				stdin=subprocess.PIPE,
				stdout=subprocess.PIPE,
			)
			for name, description in tags:
				fzf_search.stdin.write(
					bytes(f"{name}\t{description}\n", encoding="utf8")
				)
			fzf_search.stdin.close()
			while fzf_search.returncode is None:
				fzf_search.poll()
			tag_and_query = fzf_search.stdout.read().decode("utf8").strip().split("\n", 1)
			self.tag.name = (
				tag_and_query[1].split("\t")[0].strip()
				if len(tag_and_query) == 2
				else tag_and_query[0].strip()
			)
			self.tag.polarity = True
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
				if self.tag.polarity:
					modified = self.tag.name not in tags
					tags.add(self.tag.name)
				else:
					modified = self.tag.name in tags
					tags.discard(self.tag.name)
				file_annotations["tags"] = sorted(tags)
				with open(file_annotations_path, "w") as f:
					JSON.dump(file_annotations, f)
				if modified:
					print(fa.as_id())
		else:
			raise ValueError("""
				Tagging things by search is not yet supported, because Seán
				sometimes has to accept his tools as they are, and get his PhD
				work done :-*
			""")