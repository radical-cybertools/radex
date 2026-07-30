ROOT := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
DIRS := $(ROOT)/../example $(ROOT)/../tests

.PHONY: format lint black black-check isort isort-check

format: black isort

lint: black-check isort-check
VERBOSE ?= 0
VERBOSE_FLAG := $(if $(VERBOSE),-v,)

black:
	black $(VERBOSE_FLAG) --config $(ROOT)/style/black.toml $(DIRS)

black-check:
	black $(VERBOSE_FLAG) --config $(ROOT)/style/black.toml --check $(DIRS)

isort:
	isort $(VERBOSE_FLAG) --settings-file $(ROOT)/style/isort.toml $(DIRS)

isort-check:
	isort $(VERBOSE_FLAG) --settings-file $(ROOT)/style/isort.toml --check $(DIRS)
