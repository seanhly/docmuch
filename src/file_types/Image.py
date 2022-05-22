from file_types.FileType import FileType


class Image(FileType):
	@classmethod
	def key(cls):
		return "image"

	@classmethod
	def required_exif_mappings(cls):
		return {
			"PNG:ImageWidth": "width",
			"SVG:ImageWidth": "width",
			"PNG:ImageHeight": "height",
			"SVG:ImageHeight": "height",
		}

	@classmethod
	def required_fields(cls):
		return set()

	@classmethod
	def suffixes(cls):
		return {
			"PNG", "SVG"
		}