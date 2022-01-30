SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
MAKEFLAGS += --warn-undefined-variables --no-builtin-rules

.PHONY: build
PACKAGE=image_sort

build:
	python3 -m build

install:
	python3 -m pip install .

