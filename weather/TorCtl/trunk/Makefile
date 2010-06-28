
TOR=$(HOME)/src/tor
SPEC=$(TOR)/doc/control-spec.txt

VERSION=0.1-cvs
DOCS=doc/howto.txt TODO README
JAVA=`find java -name '*.java'`
PYTHON=`find python -name '*py'`
BUILD=Makefile
DISTFILES=$(DOCS) $(JAVA) $(PYTHON) $(BUILD)

all: jar

jar:
	rm -rf classes
	mkdir classes
	(cd java && javac -d ../classes net/freehaven/tor/control/*.java \
	                              net/freehaven/tor/control/*/*.java )
	jar cf torctl.jar -C classes .

dist: clean
	rm -rf torctl-$(VERSION)
	mkdir torctl-$(VERSION)
	tar cf - $(DISTFILES) | (cd torctl-$(VERSION); tar xf -)
	cp $(SPEC) torctl-$(VERSION)/doc
	tar czf torctl-$(VERSION).tar.gz torctl-$(VERSION)
	rm -rf torctl-$(VERSION)

clean:
	rm -rf classes
	find . -name '*~' -print0 |xargs -0 rm
	find . -name '*.py[co]' -print0 |xargs -0 rm
	find . -name '*.class' -print0 |xargs -0 rm
