from JSON import JSON
import subprocess


def get_metadata(file_names):
	if file_names:
		CMD = "/usr/bin/exiftool"
		metadata = JSON.loads(subprocess.check_output(
			[CMD, "-G", "-j", "-n", *file_names],
			stderr=subprocess.DEVNULL
		))
	else:
		metadata = []
	return metadata
