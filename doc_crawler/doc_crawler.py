#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Name: doc_crawler.py
# Author: Simon Descarpentries
# Licence: GPLv3

from sys import argv, stderr
from random import randint
from time import sleep
from urllib.parse import urljoin
import requests, re, logging, logging.config, yaml, datetime


__all__ = ['doc_crawler', 'download_files', 'download_file', 'run_cmd']
WANTED_EXT = '\.(pdf|docx?|xlsx?|pptx?|o(d|t)[cgmpst]|csv|rtf|zip|rar|t?gz|xz)$'
BIN_EXT = '\.?(jpe?g|png|gif|ico|bmp|swf|flv|mpe?.|h26.|avi|m.v|flac|zip|rar|t?gz|xz|js)$'


def run_cmd(argv):
	"""  Explore a website recursively from a given URL and download all the documents matching
	a regular expression.

	Documents can be listed to the output or downloaded (with the --download argument).

	To address real life situations, activities can be logged (with --verbose).
	Also, the search can be limited to a single page (with the --single-page argument).

	Else, documents can be downloaded from a given list of URL (that you may have previously
	produced using `doc_crawler`), and you can finish the work downloading documents one by one
	if necessary.

	By default, the program waits a randomly-pick amount of seconds, between 1 and 5 before each
	downloads. This behavior can be disabled (with a --no-random-wait and/or --wait=0 argument).
	"""

	USAGE = """\nUsages:
	doc_crawler.py [--accept=jpe?g$] [--download] [--single-page] [--verbose] http://…
	doc_crawler.py [--wait=3] [--no-random-wait] --download-files url.lst
	doc_crawler.py [--wait=0] --download-file http://…

	or

	python3 -m doc_crawler […] http://…
	"""
	regext = WANTED_EXT
	do_dl = False
	do_journal = False
	do_wait = 5
	do_random_wait = True
	single_page = False

	for i, arg in enumerate(argv):
		if i == 0:  # 1st arg of argv is the program name
			continue
		elif arg.startswith('--accept'):
			regext = arg[len('--accept='):]
		elif arg == '--download':
			do_dl = True
		elif arg == '--single-page':
			single_page = True
		elif arg == '--verbose':
			do_journal = True
		elif arg.startswith('--wait'):
			do_wait = int(arg[len('--wait='):])
		elif arg == '--no-random-wait':
			do_random_wait = False
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
		elif arg.startswith('--test'):
			import doctest
			doctest.run_docstring_examples(globals()[arg[len('--test='):]], globals())
			raise SystemExit()
		else:
			raise SystemExit("Unrecognized argument: "+arg+"\n"+USAGE)

	if len(argv) < 2:
		raise SystemExit("Missing argument\n"+USAGE)

	doc_crawler(argv[-1], regext, do_dl, do_journal, single_page)


def doc_crawler(base_url, wanted_ext=WANTED_EXT, do_dl=False, do_journal=False,
		do_wait=False, do_random_wait=False, single_page=False):
	"""
	For more information, see help(run_cmd) and README.md

	>>> url='https://github.com/Siltaar/doc_crawler.py/blob/master/doc_crawler/test/'
	>>> doc_crawler(url, '/raw/', do_wait=1)  # doctest: +ELLIPSIS
	https://.../raw/master/doc_crawler/test/test_a.txt
	https://.../raw/master/doc_crawler/test/test_b.txt
	https://.../raw/master/doc_crawler/test/test_c.txt
	https://.../raw/master/doc_crawler/test/test_doc.lst
	>>> doc_crawler(url, '/raw/', do_wait=0, single_page=1)
	>>> doc_crawler(url+'test_a.txt', '/raw/', single_page=1)  # doctest: +ELLIPSIS
	https://.../raw/master/doc_crawler/test/test_a.txt
	"""
	journal = 0

	if do_journal:
		logging.config.dictConfig(yaml.load(LOGGING))
		journal = logging.getLogger('journal')

	found_pages_list = [base_url]
	found_pages_set = set(found_pages_list)
	regurgited_pages = set()
	caught_docs = set()

	for page_url in found_pages_list:
		do_wait and controlled_sleep(do_wait, do_random_wait)
		do_journal and journal.info("tries page " + page_url)

		try:
			page = requests.get(page_url, stream=True)
		except Exception as e:
			do_journal and journal.error(e)
			stderr(e)
			continue

		if (page.status_code == requests.codes.ok and
				re.search('text/(html|css)', page.headers['content-type'], re.I)):
			found_pages_list, found_pages_set, regurgited_pages, caught_docs = explore_page(
				base_url, page_url, str(page.content), wanted_ext, journal, do_dl,
				found_pages_list, found_pages_set, regurgited_pages, caught_docs)

		page.close()

		if single_page:
			break

	if do_journal:
		journal.info("found %d pages, %d doc(s)" % (len(found_pages_set), len(caught_docs)))


def explore_page(base_url, page_url, page_str, wanted_ext, journal, do_dl,
		found_pages_list, found_pages_set, regurgited_pages, caught_docs):
	"""
	>>> W = WANTED_EXT
	>>> ht = 'http://'
	>>> explore_page('', '', '', WANTED_EXT, 0, 0, [], set(), set(), set())
	([], set(), set(), set())
	>>> explore_page('http://a.fr','http://a.fr/b','href="c.htm"', W,0,0,[],set(),set(),set())
	(['http://a.fr/c.htm'], {'http://a.fr/c.htm'}, set(), set())
	>>> explore_page('http://a.fr','http://a.fr/b','href="c.pdf"', W,0,0,[],set(),set(),set())
	http://a.fr/c.pdf
	([], set(), set(), {'http://a.fr/c.pdf'})
	>>> explore_page('http://a.fr','http://a.fr/b','href="c.JPG"', W,0,0,[],set(),set(),set())
	([], set(), {'http://a.fr/c.JPG'}, set())
	>>> explore_page(ht+'a.fr','http://a.fr/b','src="c.JPG"',  'JPG',0,0,[],set(),set(),set())
	http://a.fr/c.JPG
	([], set(), set(), {'http://a.fr/c.JPG'})
	>>> explore_page(ht+'a.fr','http://a.fr/b','src="c.css"',      W,0,0,[],set(),set(),set())
	(['http://a.fr/c.css'], {'http://a.fr/c.css'}, set(), set())
	>>> explore_page(ht+'a.fr','http://a.fr/b','url("c.JPG")', 'JPG',0,0,[],set(),set(),set())
	http://a.fr/c.JPG
	([], set(), set(), {'http://a.fr/c.JPG'})
	>>> explore_page('http://a.fr','http://a.fr/b','href="httpc"', W,0,0,[],set(),set(),set())
	(['http://a.fr/httpc'], {'http://a.fr/httpc'}, set(), set())
	>>> explore_page('http://a.fr','http://a.fr/b/c','href="d"',   W,0,0,[],set(),set(),set())
	(['http://a.fr/b/d'], {'http://a.fr/b/d'}, set(), set())
	>>> explore_page(ht+'a.fr','http://a.fr','href="b"href="c"',   W,0,0,[],set(),set(),set())
	... # doctest: +ELLIPSIS
	(['http://a.fr/b', 'http://a.fr/c'], {...}, set(), set())
	>>> explore_page(ht+'a.fr',ht+'a.fr','href="http://a.fr/b"',   W,0,0,[],set(),set(),set())
	(['http://a.fr/b'], {'http://a.fr/b'}, set(), set())
	>>> explore_page(ht+'a.fr',ht+'a.fr','href="'+ht+'a.fr/b.pdf"',W,0,0,[],set(),set(),set())
	http://a.fr/b.pdf
	([], set(), set(), {'http://a.fr/b.pdf'})
	>>> explore_page(ht+'a.fr','http://a.fr','href=""', W,0,0,[],set([ht+'a.fr']),set(),set())
	([], {'http://a.fr'}, set(), set())
	>>> explore_page(ht+'a.fr',ht+'a.fr','href="javascript:;"',	   W,0,0,[],set(),set(),set())
	([], set(), {'javascript:;'}, set())
	>>> explore_page(ht+'a.fr',ht+'a.fr','href="mailto:a@a.fr"',   W,0,0,[],set(),set(),set())
	([], set(), {'mailto:a@a.fr'}, set())
	>>> explore_page('http://a.fr','http://a.fr/b/','href="c/d"',  W,0,0,[],set(),set(),set())
	(['http://a.fr/b/c/d'], {'http://a.fr/b/c/d'}, set(), set())
	>>> explore_page('http://a.fr','http://a.fr/?b=c','href="d"',  W,0,0,[],set(),set(),set())
	(['http://a.fr/d'], {'http://a.fr/d'}, set(), set())
	>>> explore_page(ht+'a.fr','http://a.fr/?b=c','href="?d=e"',   W,0,0,[],set(),set(),set())
	(['http://a.fr/?d=e'], {'http://a.fr/?d=e'}, set(), set())
	"""
	# extract links
	for a_href in re.finditer('(href|src)="(.*?)"|url\("?\'?(.*?)\'?"?\)', page_str, re.I):
		a_href = a_href.group(a_href.lastindex)

		if not re.search('^https?://', a_href):  # if it's a relative link
			a_href = urljoin(page_url, a_href)

		if re.search(wanted_ext, a_href, re.I) and a_href not in caught_docs:  # wanted doc ?
			caught_docs.add(a_href)
			do_dl and download_file(a_href) or print(a_href)
		elif base_url in a_href and not re.search(BIN_EXT, a_href, re.I):  # next page ?
			if a_href not in found_pages_set:
				journal and journal.info("will explore "+a_href)
				found_pages_list.append(a_href)
				found_pages_set.add(a_href)
		elif a_href not in regurgited_pages:  # junk link ?
			journal and journal.debug("regurgited link "+a_href)
			regurgited_pages.add(a_href)

	return found_pages_list, found_pages_set, regurgited_pages, caught_docs


def controlled_sleep(seconds=1, do_random_wait=False):
	""" Waits the given number of seconds (or a random one between 1 and it). """
	sleep(randint(1, seconds) if do_random_wait else seconds)


def download_file(URL, do_wait=False, do_random_wait=False):
	""" Directly retrieves and writes in the current folder the pointed URL.
	>>> download_file('https://github.com/Siltaar/doc_crawler.py/blob/master/test/test_a.txt')
	"""
	do_wait and controlled_sleep(do_wait, do_random_wait)
	with open(URL.split('/')[-1], 'wb') as f:
		f.write(requests.get(URL, stream=True).content)


def download_files(URLs_file, do_wait=False, do_random_wait=False):
	""" Downloads files which URL are listed in the pointed file.
	>>> download_files('test/test_doc.lst')  # doctest: +ELLIPSIS
	download 1 - https://.../blob/master/doc_crawler/test/test_a.txt
	download 2 - https://.../blob/master/doc_crawler/test/test_b.txt
	download 3 - https://.../blob/master/doc_crawler/test/test_c.txt
	downloaded 3 / 3
	"""
	line_nb = 0
	downloaded_files = 0

	with open(URLs_file) as f:
		for line in f:
			line = line.rstrip('\n')

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
		journal:
			handlers: ['journal']
			level: DEBUG
""".format(cur_dt=datetime.datetime.now().isoformat())


if __name__ == '__main__':
	run_cmd(argv)
