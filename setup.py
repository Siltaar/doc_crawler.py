#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import doc_crawler
from setuptools import setup, find_packages

setup(
	name='doc_crawler',
	version=doc_crawler.__version__,
	packages=find_packages(),
	author="Simon Descarpentries",
	author_email="contact@acoeuro.com",  # will be public
	description="Explore a website recursively and download all the wanted documents "
	"(PDF, ODT…)",
	long_description=open('README.asciidoc').read(),
	include_package_data=True,  # take MANIFEST.in into account
	url='https://github.com/Siltaar/doc_crawler.py',
	classifiers=[  # https://pypi.python.org/pypi?%3Aaction=list_classifiers.
		"Development Status :: 5 - Production/Stable",
		"Programming Language :: Python :: 3",
		"Operating System :: OS Independent",
		"Topic :: Internet :: WWW/HTTP",
		"Intended Audience :: End Users/Desktop",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)"
	],
	keywords='crawler downloader recursive pdf-extractor web-crawler web-crawler-python '
	'file-download pdf zip doc odt',
	python_requires='>=3',
	# entry_points={
	#	'console_scripts': [
	#		'doc_crawler.py = doc_crawler.doc_crawler:run_cmd',  # doc_crawler is not a package
	#	],
	# },
)
