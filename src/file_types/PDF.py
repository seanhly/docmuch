import re
import subprocess
from file_types.FileType import FileType
from third_party_modules import dateparser, grobid_tei_xml
from os.path import exists
from urllib import request as request
import subprocess
from PreIndexFunctions import PreIndexFunctions


class PDF(FileType):
	@classmethod
	def get_info(cls, file):
		CMD = '/usr/bin/pdfinfo'
		if not exists(CMD):
			raise RuntimeError('System command not found: %s' % CMD)
		if not exists(file):
			raise RuntimeError('Provided input file not found: %s' % file)
		pdf_info = {}
		cmd_output = subprocess.check_output([CMD, file])
		output = cmd_output.decode().strip()
		lines = output.split("\n")
		i = 0
		while i < len(lines):
			line = lines[i]
			if ":" not in line:
				lines = lines[:i-1] + [f"{lines[i - 1]} {lines[i]}"] + lines[i+1:]
			else:
				i += 1
		for line in lines:
			key, value = map(str.strip, line.split(":", 1))
			if key == "Pages":
				pdf_info["pages"] = int(re.sub("[^0-9]", "", value))
			if key == "CreationDate":
				pdf_info["created"] = int(dateparser.parse(value).timestamp())
			if key == "Title":
				pdf_info["title"] = value
			if key == "Author":
				pdf_info["author"] = value
			if key == "Keywords":
				pdf_info["keywords"] = value
			if key == "Subject":
				pdf_info["subject"] = value
		tei_info = PDF.to_tei(file)
		pdf_info["tei"] = (
			tei_info
			if tei_info and len(tei_info) > 0
			else None
		)
		return pdf_info

	def to_text(file):
		CMD = '/usr/bin/pdftotext'
		if not exists(CMD):
			raise RuntimeError('System command not found: %s' % CMD)
		if not exists(file):
			raise RuntimeError('Provided input file not found: %s' % file)
		return subprocess.check_output(
			[CMD, "-layout", file, "-"],
			stderr=subprocess.DEVNULL
		).decode().strip()

	def to_tei(file):
		CMD = '/usr/bin/curl'
		if not exists(CMD):
			raise RuntimeError('System command not found: %s' % CMD)
		if not exists(file):
			raise RuntimeError('Provided input file not found: %s' % file)
		try:
			tei_str = subprocess.check_output(
				[
					CMD, "-s", "--form", f"input=@\"{file}\"", "-X", "POST",
					"http://127.0.0.1:8070/api/processFulltextDocument"
				],
				stderr=subprocess.DEVNULL
			).decode()
			if tei_str:
				tei = grobid_tei_xml.parse_document_xml(tei_str).to_dict()
				tei_info = {}
				tei_header = tei.get("header", {})
				if "language_code" in tei:
					tei_info["language"] = tei["language_code"]
				if "body" in tei:
					tei_info["body"] = tei["body"]
				if "title" in tei_header:
					tei_info["title"] = tei_header["title"]
				if "abstact" in tei:
					tei_info["abstract"] = tei["abstact"]
				if "acknowledgement" in tei:
					tei_info["acknowledgement"] = tei["acknowledgement"]
				if "date" in tei_header:
					tei_info["date"] = tei_header["date"]
				if "authors" in tei_header:
					tei_info["authors"] = [
						PDF.author_to_dict(a)
						for a in tei_header["authors"]
					]
				if "citations" in tei:
					tei_info["citations"] = [
						PDF.citation_to_string(c)
						for c in tei["citations"]
					]
			else:
				tei_info = None
		except Exception as e:
			tei_info = None
		return tei_info

	def author_to_dict(a):
		d = dict(
			name=a.get("full_name", ""),
		)
		if "email" in a:
			d["email"] = a["email"]
		if "affiliation" in a:
			affiliation = a["affiliation"]
			the_address = []
			if "department" in affiliation:
				the_address.append(affiliation["department"])
			if "institution" in affiliation:
				the_address.append(affiliation["institution"])
			if "address" in affiliation:
				address = affiliation["address"]
				if "addr_line" in address:
					the_address.append(address["addr_line"])
				if "post_code" in address:
					the_address.append(address["post_code"])
				if "settlement" in address:
					the_address.append(address["settlement"])
				if "country" in address:
					the_address.append(address["country"])
			if the_address:
				d["address"] = the_address
		return d

	def citation_to_string(c):
		s = ""
		if "book_title" in c:
			s = c["book_title"]
			if "title" in c:
				s += ": " + c["title"]
		else:
			if "title" in c:
				s += c["title"]
		if "authors" in c:
			parsed_authors = [
				PDF.author_to_dict(a)
				for a in c["authors"]
			]
			authors = PreIndexFunctions.parsed_authors_to_strings(
				parsed_authors, sep=", "
			)
			s += ", " + ", ".join(authors)
		if "journal" in c:
			s += ", " + c["journal"]
		if "volume" in c:
			s += ", Volume " + c["volume"]
		if "issue" in c:
			s += ", Issue " + c["issue"]
		if "pages" in c:
			s += ", Pages " + c["pages"]
		if "date" in c:
			s += ", " + c["date"]
		return s

	@classmethod
	def key(cls):
		return "pdf"

	@classmethod
	def non_keys(cls):
		return {
			"book",
		}

	@classmethod
	def required_exif_mappings(cls):
		return {
    		"PDF:Title": "title",
    		"PDF:Language": "language",
    		"PDF:PageCount": "pages",
    		"XMP:Keywords": "keywords",
    		"XMP:Title-en": "title",
    		"XMP:Title": "title",
    		"XMP:Publisher": "publisher",
    		"XMP:Date": "date",
			"XMP:Creator": "creators",
			"XMP:Subject": "subject",
			"XMP:Source": "source",
			"XMP:Language": "language",
    		"XMP:CreatorCity": "city",
    		"XMP:CreatorCountry": "country",
    		"XMP:CreatorWorkEmail": "email",
    		"XMP:PublicationName": "publication",
		}

	@classmethod
	def required_fields(cls):
		return {
			"tei",
		}

	@classmethod
	def non_keys(cls):
		return {
			"image",
			"music",
			"tei",
		}

	@classmethod
	def suffixes(cls):
		return {"PDF"}
