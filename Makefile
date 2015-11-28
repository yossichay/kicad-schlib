LIBFILES=$(wildcard library/*.lib)
DCMFILES=$(patsubst %.lib,%.dcm,${LIBFILES})
PVFILES=$(addprefix preview/,$(patsubst %.lib,%.md,$(notdir ${LIBFILES})))
IMAGECACHE:=$(shell mktemp)
DBFILES=$(shell find bomtool-db -type f)

TMPDIR := $(shell mktemp -d)

BOMTOOL ?= $$(which bomtool)

.PHONY: all dcmfiles bom_check

%.dcm: %.lib ${DBFILES}
	@echo $<
	@./scripts/libfile_tool.py import_descrs $^ <$@ >${TMPDIR}/$$(basename $@)
	@mv ${TMPDIR}/$$(basename $@) $@

all: ${PVFILES} ${DCMFILES}
	rm -f ${IMAGECACHE}
	@#./scripts/cleanup.py images

dcmfiles: ${DCMFILES}

bom_check: ${LIBFILES}
	for f in ${LIBFILES}; do \
		./scripts/libfile_tool.py bom_check $$f $$(which bomtool); \
	done

preview/%.md: library/%.lib
	mkdir -p preview/images
	if [ -f $(patsubst %.lib,%.dcm,$<) ]; then \
		./scripts/schlib-render.py preview/images /images ${IMAGECACHE} $< $(patsubst %.lib,%.dcm,$<) > $@; \
	else \
		./scripts/schlib-render.py preview/images /images ${IMAGECACHE} $< > $@; \
	fi
