VERSION=0.1-cvs
LIBSRC=control/*.cs \
       control/ControlConnectionClasses/*.cs \
       control/Exceptions/*.cs \
       control/HelperClasses/*.cs
       
TESTSRC=test/*.cs
     
all: test 

dll: clean
	mkdir bin
	mcs -target:library -out:bin/Tor.Control.dll $(LIBSRC)

test: dll
	mcs -target:exe -out:bin/test.exe -reference:bin/Tor.Control.dll $(TESTSRC)

clean:
	rm -rf bin
