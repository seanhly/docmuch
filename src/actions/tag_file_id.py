from os.path import join, exists
from constants import FILE_ANNOTATIONS_PATH
from urllib import request as request
from JSON import JSON


def tag_file_id(actual_tag, file_id, remove = False):
	file_annotations_path = join(FILE_ANNOTATIONS_PATH, f"{file_id}.json")
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
	if remove:
		modified = actual_tag in tags
		tags.discard(actual_tag)
	else:
		modified = actual_tag not in tags
		tags.add(actual_tag)
	file_annotations["tags"] = sorted(tags)
	file_content = JSON.dumps(file_annotations)
	with open(file_annotations_path, "w") as f:
		f.write(file_content)
	return modified
