import json
from file_types.FileType import FileType
from typing import Dict
from os.path import join


class Recipe(FileType):
	@classmethod
	def view_path(cls, fa: "FileLikeArgument") -> str:
		html_path = join("/tmp", f"{fa.as_id()}.html")
		with open(html_path, "w") as w:
			with open(fa.as_full_typed_file_path(cls), "r") as r:
				content = r.read().strip()
				j = json.loads(content)
				print(j['image'])
				header = """
				<style>
				img {
					max-width: 100%;
					height: 200px;
				}
				body {
					max-width: 100%;
					margin: auto;
					font-size: 2em;
				}
				</style>
				<body>""" + f"<img src='{j['image']}'><pre>"
				w.write(header)
				def print_pre_line(lines=""):
					for line in lines.split("\n"):
						w.write(f"   {line}\n")
				print_pre_line(j['title'])
				print_pre_line(len(j['title']) * "=")
				print_pre_line()
				print_pre_line("Ingredients")
				print_pre_line("-----------")
				print_pre_line()
				print(2)
				def print_li(txt, i=None):
					lines = []
					line = ""
					for w in txt.split():
						if len(line) + len(w) + 1 > 50:
							lines.append(line)
							line = w
						else:
							line += " " + w
					if line:
						lines.append(line)
					if i:
						txt = "\n   ".join(lines)
					else:
						txt = "\n  ".join(lines)
					if i:
						print_pre_line(f"{i}.{txt}\n")
					else:
						print_pre_line(f"-{txt}\n")
				for ingredient in j['ingredients']:
					print_li(ingredient)
				print_pre_line("Method")
				print_pre_line("------")
				print_pre_line()
				for i, step in enumerate(j['method'], start=1):
					print_li(step, i)
				w.write("</pre>")

		return html_path

	@classmethod
	def get_info(cls, fa):
		with open(fa.as_full_typed_file_path(cls), "r") as f:
			content = f.read().strip()
			return json.loads(content)

	@classmethod
	def key(cls):
		return "recipe"

	@classmethod
	def required_fields(cls):
		return set()


	@classmethod
	def required_exif_mappings(cls) -> Dict[str, str]:
		return {}

	@classmethod
	def suffixes(cls):
		return {"RECIPE"}

	@classmethod
	def view_cmd(cls) -> str:
		return "/usr/bin/dillo -f"