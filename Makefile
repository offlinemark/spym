SRC = $(wildcard *.py)
LIB = emu util

MAIN = __main__.pyo
OUT = bin
ZIP = zip
PYCC = python2.7 -OO -m py_compile


default: bin $(SRC:.py=.zip)

BIN = $(OUT)/$@
%.zip: %.pyo
	ln -s $< $(MAIN)
	$(ZIP) -r $(BIN) $(MAIN) $(LIB)
	rm $(MAIN)
	cp $(BIN) .tmp
	echo "#!/usr/bin/env python2.7" > $(BIN)
	cat .tmp >> $(BIN)
	rm .tmp
	chmod +x $(BIN)
	mv $(BIN) $(basename $(BIN))

%.pyo: %.py
	$(PYCC) $<

bin:
	mkdir bin
