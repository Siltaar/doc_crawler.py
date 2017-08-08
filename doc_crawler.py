#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Name: doc_crawler.py
# Author: Simon Descarpentries
# Licence: GPLv3

from sys import argv, stderr
from lxml import html
from random import randint
from time import sleep
from urllib.parse import urljoin
import requests, re, logging, logging.config, yaml, datetime


LOGGING = """
	version: 1
	disable_existing_loggers: False
	formatters:
		local:
			format: '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s'
	handlers:
		journal:
			class: logging.FileHandler
			formatter: local
			filename: {cur_dt}_journal.log
			encoding: utf-8
	loggers:
		results:
			handlers: ['results']
			level: DEBUG
""".format(cur_dt=datetime.datetime.now().isoformat())
WANTED_EXT = '\.(pdf|docx?|xlsx?|od[ts]|csv|rtf)'


def crawl_web_for_files(starting_URL, wanted_ext=WANTED_EXT, do_dl=False, do_journal=False,
		do_wait=False, do_random_wait=False):
	""" Explore a website recursively from a given URL and retrieve, in the descendant pages,
	the encountered document files (by default PDF, ODT, CSV, RTF, DOC and XLS) based on their
	extension.

	It can directly download found documents, or output their URL to pipe them somewhere else.

	It can also be used to directly download a single file or a list files."""
	if do_journal:
		logging.config.dictConfig(yaml.load(LOGGING))
		journal = logging.getLogger('journal')

	BIN_EXT = '\.?(jpe?g|png|gif|swf)'
	found_pages_list = [starting_URL]
	found_pages_set = set(found_pages_list)
	regurgited_pages = set()
	caught_docs = set()

	for f in found_pages_list:
		if do_wait:
			controlled_sleep(do_wait, do_random_wait)

		if do_journal:
			journal.info("tries page " + f)

		try:
			page = requests.get(f)
		except Exception as e:
			if do_journal:
				journal.error(e)

			stderr(e)
			continue

		tree = html.fromstring(page.content)

		for a in tree.cssselect('a'):  # explore current page links
			a_href = a.get('href', '')
			a_href_ext = a_href[-4:]

			if not re.search('^https?://', a_href):  # if it's a relative link
				a_href = urljoin(f, a_href)

			# is it a link to a wanted doc ?
			if re.search(wanted_ext, a_href_ext, re.I) and a_href not in caught_docs:
				caught_docs.add(a_href)

				if do_dl:
					download_file(a_href)
				else:
					print(a_href)

			# else is it an internal link and not an image or other unparsable files
			elif starting_URL in a_href and not re.search(BIN_EXT, a_href_ext, re.I):
				if a_href not in found_pages_set:
					if do_journal:
						journal.info("will explore "+a_href)

					found_pages_list.append(a_href)
					found_pages_set.add(a_href)
			elif a_href not in regurgited_pages:
				if do_journal:
					journal.debug("regurgited link "+a_href)

				regurgited_pages.add(a_href)

	if do_journal:
		journal.info("found %d pages, %d doc(s)" % (len(found_pages_set), len(caught_docs)))


def controlled_sleep(seconds=1, do_random_wait=False):
	""" Will wait the given number of seconds (or a random one between 1 and it). """
	sleep(randint(1, seconds) if do_random_wait else seconds)


def download_file(URL, do_wait=False, do_random_wait=False):
	""" Will directly retrieve and write in the current folder the pointed URL. """
	if do_wait:
		controlled_sleep(do_wait, do_random_wait)

	with open(URL.split('/')[-1], 'wb') as f:
		f.write(requests.get(URL, stream=True).content)


def download_files(URLs_file, do_wait=False, do_random_wait=False):
	""" Will download files which URL are listed in the pointed file. """
	line_nb = 0
	downloaded_files = 0

	with open(URLs_file) as f:
		for line in f:
			if line is '':
				continue

			line_nb += 1
			print('download %d - %s' % (line_nb, line))

			try:
				download_file(line, do_wait, do_random_wait)
				downloaded_files += 1
			except Exception as e:
				stderr(e)

	print('downloaded %d / %d' % (downloaded_files, line_nb))


if __name__ == '__main__':
	USAGE = """Usage:
	{name} [--accept=jpe?g] [--download] [--verbose] [--wait=5] [--random-wait] http://…
	{name} [--wait=5] [--random-wait] --download-file http://…
	{name} [--wait=5] [--random-wait] --download-files url.lst
	""".format(name=argv[0])
	regext = WANTED_EXT
	do_dl = False
	do_journal = False
	do_wait = False
	do_random_wait = False

	for i, arg in enumerate(argv):
		if i == 0:  # 1st arg of argv is the program name
			continue
		elif arg.startswith('--accept'):
			regext = arg[len('--accept='):]
		elif arg == '--download':
			do_dl = True
		elif arg == '--verbose':
			do_journal = True
		elif arg.startswith('--wait'):
			do_wait = int(arg[len('--wait='):])
		elif arg == '--random-wait':
			do_random_wait = True
		elif arg.startswith('http'):
			continue
		elif arg == '--download-file':
			if len(argv) < 3:
				raise SystemExit("Missing argument\n"+USAGE)
			else:
				download_file(argv[-1], do_wait, do_random_wait)
				raise SystemExit
		elif arg == '--download-files':
			if len(argv) < 3:
				raise SystemExit("Missing argument\n"+USAGE)
			else:
				download_files(argv[-1], do_wait, do_random_wait)
				raise SystemExit
		elif arg == '--help':
			raise SystemExit(USAGE)
		else:
			raise SystemExit("Unrecognized argument: "+arg+"\n"+USAGE)

	if len(argv) < 2:
		raise SystemExit("Missing argument\n"+USAGE)

	crawl_web_for_files(argv[-1], regext, do_dl, do_journal)
