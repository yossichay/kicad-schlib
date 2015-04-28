LIBFILES=$(wildcard library/*.lib)
DCMFILES=$(patsubst %.lib,%.dcm,${LIBFILES})
PVFILES=$(addprefix preview/,$(patsubst %.lib,%.md,$(notdir ${LIBFILES})))
IMAGECACHE:=$(shell mktemp)
DBFILES=$(wildcard bomtool-db/*)

TMPDIR := $(shell mktemp -d)

.PHONY: all dcmfiles

%.dcm: %.lib ${DBFILES}
	./scripts/import-descrs.py $^ <$@ >${TMPDIR}/$$(basename $@)
	mv ${TMPDIR}/$$(basename $@) $@

all: ${PVFILES} ${DCMFILES}
	rm -f ${IMAGECACHE}
	@#./scripts/cleanup.py images

dcmfiles: ${DCMFILES}

preview/%.md: library/%.lib
	if [ -f $(patsubst %.lib,%.dcm,$<) ]; then \
		./scripts/schlib-render.py images /images ${IMAGECACHE} $< $(patsubst %.lib,%.dcm,$<) > $@; \
	else \
		./scripts/schlib-render.py images /images ${IMAGECACHE} $< > $@; \
	fi
