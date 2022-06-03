from os.path import realpath, join
import subprocess
from os import environ, listdir
from typing import Dict
from JSON import JSON
from actions.Action import Action
from actions.Index import Index
from os.path import exists
from urllib import request as request


class Tag(Action):
	tag: "TagArgument" = None

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
	
	@staticmethod
	def read_tag():
		annotations_dir = realpath(join(
			environ.get("HOME"),
			"Documents",
			"FileAnnotations"
		))
		tags_path = realpath(join(
			environ.get("HOME"),
			"Documents",
			"tags.tsv"
		))
		tags: Dict[str, int] = {}
		for f in listdir(annotations_dir):
			an_annotation_for_a_file = join(annotations_dir, f)
			with open(an_annotation_for_a_file, "r") as f:
				j = JSON.load(f)
				for t in j.get("tags", []):
					tags[t] = tags.get(t, 0) + 1
		with open(tags_path, "r") as f:
			described_tags = dict(
				[
					l.strip().split("\t")
					for l in f.read().strip().split("\n")
				]
			)
		tags_by_counts = sorted([
			"\t".join(
				str(i)
				for i in (c, t, described_tags.get(t))
				if i
			)
			for t, c in tags.items()
		])
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
		for line in tags_by_counts:
			fzf_search.stdin.write(
				bytes(f"{line}\n", encoding="utf8")
			)
		fzf_search.stdin.close()
		fzf_search.wait()
		selection = fzf_search.stdout.read().decode("utf8").strip().split("\n", 1)
		if len(selection) == 2:
			tag = selection[-1].strip().split("\t")[1]
		else:
			tag = selection[-1].strip()
		
		return tag
	
	def execute(self):
		from arguments.TagArgument import TagArgument
		self.tag = TagArgument(Tag.read_tag(), True)
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
			Index(self.file_arguments).execute()
		else:
			raise ValueError("""
				Tagging things by search is not yet supported, because Seán
				sometimes has to accept his tools as they are, and get his PhD
				work done :-*
			""")