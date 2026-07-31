ROOT := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
DIRS := $(ROOT)/../example $(ROOT)/../tests

PYTEST_ARGS ?=

.PHONY: format lint black black-check isort isort-check test

format: black isort

lint: black-check isort-check
VERBOSE ?= 0
VERBOSE_FLAG := $(if $(VERBOSE),-v,)

black:
	black $(VERBOSE_FLAG) --config $(ROOT)/radex-config.toml $(DIRS)

black-check:
	black $(VERBOSE_FLAG) --config $(ROOT)/radex-config.toml --check $(DIRS)

isort:
	isort $(VERBOSE_FLAG) --settings-file $(ROOT)/radex-config.toml $(DIRS)

isort-check:
	isort $(VERBOSE_FLAG) --settings-file $(ROOT)/radex-config.toml --check $(DIRS)

test:
	dragon -s -- -m pytest $(PYTEST_ARGS) -c $(ROOT)/radex-config.toml $(ROOT)/../tests