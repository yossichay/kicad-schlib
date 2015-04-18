LIBFILES=$(wildcard library/*.lib)
DCMFILES=$(patsubst %.lib,%.dcm,${LIBFILES})
PVFILES=$(addprefix preview/,$(patsubst %.lib,%.md,$(notdir ${LIBFILES})))

.PHONY: all

all: ${PVFILES}
	./scripts/cleanup.py images

preview/%.md: library/%.lib
	if [ -f $(patsubst %.lib,%.dcm,$<) ]; then \
		./scripts/schlib-render.py images /images $< $(patsubst %.lib,%.dcm,$<) > $@; \
	else \
		./scripts/schlib-render.py images /images $< > $@; \
	fi
