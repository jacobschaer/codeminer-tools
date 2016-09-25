#!/bin/sh
command -v coverage >/dev/null && coverage erase
command -v python-coverage >/dev/null && python-coverage erase
nosetests -w codeminer --with-coverage --cover-package=codeminer $*

# Make sure svnserve dies in case tests stop early
pkill -9 svnserve