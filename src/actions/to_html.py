import json

def to_html(file: str):
	suffix = file.split("/")[-1].split(".", 1)[-1].upper()
	if suffix == "RECIPE":
		with open(file, "r") as f:
			content = f.read().strip()
			j = json.loads(content)
			print("""
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
			<body>
			""")
			print(f"<img src='{j['image']}'>")
			print("<pre>")
			def print_pre_line(lines=""):
				for line in lines.split("\n"):
					print("   " + line)
			print_pre_line(j['title'])
			print_pre_line(len(j['title']) * "=")
			print_pre_line()
			print_pre_line("Ingredients")
			print_pre_line("-----------")
			print_pre_line()
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
			print("</pre>")
