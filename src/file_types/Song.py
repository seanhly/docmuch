from file_types.FileType import FileType


class Song(FileType):
	@classmethod
	def key(cls):
		return "song"

	@classmethod
	def required_exif_mappings(cls):
		return {
			"Composite:Duration": "duration",
			"Vorbis:Album": "album",
			"Vorbis:Artist": "artist",
			"Vorbis:Date": "date",
			"Vorbis:Discnumber": "disc",
			"Vorbis:Genre": "genre",
			"Vorbis:Title": "title",
			"Vorbis:TrackNumber": "track",
			"Vorbis:Tracktotal": "total-tracks",
		}

	@classmethod
	def required_fields(cls):
		return set()

	@classmethod
	def suffixes(cls):
		return {"OGG"}