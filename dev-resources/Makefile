ROOT := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
DIRS := $(ROOT)/../example \
        $(ROOT)/../tests \
        $(ROOT)/../include \
        $(ROOT)/../src

HEADER_FILES = $(shell find $(DIRS) \
    -path '$(ROOT)/../src/python/build/*' -prune \
    -name '*.h' -o -name '*.hh' -o -name '*.hpp')

CPP_SRC = $(shell find $(DIRS) \
    -path '$(ROOT)/../src/python/build/*' -prune \
    -name '*.cpp' -o -name '*.cc')

C_SRC = $(shell find $(DIRS) \
    -path '$(ROOT)/../src/python/build/*' -prune \
    -name '*.c')

PYTEST_ARGS ?=
PYTHON ?= python3

.PHONY: format lint black black-check isort isort-check clang-format \
        clang-format-check test docs docs-serve

format: black isort clang-format

lint: black-check isort-check clang-format-check
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

clang-format:
	@clang-format \
        --style=file:$(ROOT)/../.clang-format \
        -i $(if $(VERBOSE),--verbose,) \
        $(HEADER_FILES) $(CPP_SRC) $(C_FILES)

clang-format-check:
	@clang-format \
        --dry-run --Werror \
        --style=file:$(ROOT)/../.clang-format \
        $(if $(VERBOSE),--verbose,) \
        $(HEADER_FILES) $(CPP_SRC) $(C_FILES)

test:
	dragon -s -- -m pytest $(PYTEST_ARGS) -c $(ROOT)/radex-config.toml $(ROOT)/../tests

docs:
	@command -v doxygen >/dev/null 2>&1 || \
		echo "warning: 'doxygen' not found on PATH; the C++ API reference will fail to build."
	cd $(ROOT)/.. && $(PYTHON) -m mkdocs build --clean

docs-serve:
	@command -v doxygen >/dev/null 2>&1 || \
		echo "warning: 'doxygen' not found on PATH; the C++ API reference will fail to build."
	cd $(ROOT)/.. && $(PYTHON) -m mkdocs serve -a 0.0.0.0:8001
