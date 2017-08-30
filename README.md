`doc_crawler` can explore a website recursively from a given URL and retrieve, in the
descendant pages, the encountered document files (by default: PDF, ODT, CSV, RTF, DOC and XLS)
based on regular expression matching (typically against their extension).

## Features
Documents can be listed on the standard output or downloaded (with the `--download` argument).

To address real life situations, activities can be logged (with `--verbose`). \
Also, the search can be limited to one page (with the `--single-page` argument).

Else, documents can be downloaded from a given list of URL, that you may have previously
produced using default options of `doc_crawler` and an output redirection such as: \
`./doc_crawler.py http://… > url.lst`.

To finish the work, documents can be downloaded one by one if necessary, using the
`--download-file` argument, which makes `doc_crawler` a tool sufficient by itself to assist you
at every steps.

By default, the program waits a randomly-pick amount of seconds, between 1 and 5, before each
download to avoid being rude toward the webserver it interacts with (and so avoid being
black-listed). This behavior can be disabled (with a `--no-random-wait` and/or a `--wait=0`
argument).

## Options
`--accept` optional regular expression (case insensitive) to keep matching document names. \
 Example : `--accept=jpe?g$` will hopefully keep all : .JPG, .JPEG, .jpg, .jpeg \
`--download` directly downloads found documents if set, output their URL if not. \
`--single-page` limits the search for documents to download to the giver URL. \
`--verbose` creates a log file to keep trace of what was done. \
`--wait=x` change the default waiting time before each download (page or document). \
 Example : `--wait=3` will wait between 1 and 3s before each download. Default is 5.\
`--no-random-wait` stops the random pick up of waiting times. `--wait=` or default is used.\
`--download-files` will download each documents which URL are listed in the given file. \
 Example : `--download-files url.lst`
`--download-file` will directly save in the current folder the URL-pointed document. \
 Example : `--download-file http://…` \

## Usages
`doc_crawler.py [--accept=jpe?g] [--download] [--single-page] [--verbose] http://…` \
`doc_crawler.py [--wait=3] [--no-random-wait] --download-files url.lst` \
`doc_crawler.py [--wait=0] --download-file http://…`

`--wait=` and `--no-random-wait` arguments can be used with every form. \
`doc_crawler.py` works great with Tor : `torsocks doc_crawler.py http://…`\
From a `pip` installed `doc_crawler` package, the command can be invoked as follow:
`python3 -m doc_crawler […] http://…`

## Tests
Around 20 doctests are included in `doc_crawler.py`. You can run them with the following
command in the cloned repository root: \
`python3 -m doctest doc_crawler.py`

Tests can also be launched one by one using the `--test=XXX` argument:\
`python3 -m doc_crawler --test=download_file`

Tests are successfully passed if nothing is output.

## Requirements
* requests
* yaml

One can install them Under Debian using the following command : `apt install python3-requests python3-yaml`

## Licence
GNU General Public License v3.0. See LICENCE file for more information.
