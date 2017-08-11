`doc_crawler` can explore a website recursively from a given URL and retrieve, in the
descendant pages, the encountered document files (by default: PDF, ODT, CSV, RTF, DOC and XLS)
based on regular expression matching (typically against their extension).

Documents can be listed to the output or downloaded (with the `--download` argument).

To address real life situation, one can log activity and follow the progress (with `--verbose`). \
Also, the search can be limited to a single page (with the `--single-page` argument).

Else, documents can be downloaded from a given list of URL (that one may have previously
produced using `doc_crawler`, and one can finish the work downloading documents one by one if
necessary.

By default, the program waits a randomly-pick amount of seconds, between 1 and 5, before each
download to avoid being rude toward the webserver `doc_crawler` interact with (and so avoid to be
black-listed). This behavior can be disabled (with a `--no-random-wait` and/or `--wait=0` argument).

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

## Usage
`doc_crawler.py [--accept=jpe?g] [--download] [--single-page] [--verbose] http://…` \
`doc_crawler.py [--wait=0] --download-files url.lst`
`doc_crawler.py [--wait=3] [--no-random-wait] --download-file http://…` \

## Test
`doc_crawler.py` includes around 20 doctests that you can run with the following command in the cloned repository root: \
`python3 -m doctest doc_crawler.py`

It should be no output.

## Requirements
* requests
* yaml

One can install them Under Debian using the following command : `apt install python3-requests python3-yaml`
