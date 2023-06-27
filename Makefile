SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
MAKEFLAGS += --warn-undefined-variables --no-builtin-rules

.PHONY: build install
PACKAGE=reimage

build:
	python3 -m build

install:
	python3 -m pip install .

all: build install

publish:
	twine upload dist/*