LIBFILES=$(wildcard library/*.lib)
DCMFILES=$(patsubst %.lib,%.dcm,${LIBFILES})
PVFILES=$(addprefix preview/,$(patsubst %.lib,%.md,$(notdir ${LIBFILES})))
IMAGECACHE:=$(shell mktemp)

.PHONY: all

all: ${PVFILES}
	rm -f ${IMAGECACHE}
	@#./scripts/cleanup.py images

preview/%.md: library/%.lib
	if [ -f $(patsubst %.lib,%.dcm,$<) ]; then \
		./scripts/schlib-render.py images /images ${IMAGECACHE} $< $(patsubst %.lib,%.dcm,$<) > $@; \
	else \
		./scripts/schlib-render.py images /images ${IMAGECACHE} $< > $@; \
	fi
