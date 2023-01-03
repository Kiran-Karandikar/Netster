CC	      = gcc
MAC_FLAGS = -O2 -Wall         -pedantic -std=gnu99
CFLAGS	  =  -O2 -Wall -Werror -pedantic -std=gnu99
LIBS	  = -lm -lpthread -no-pie

PROGRAM	  = httpcmd

$(PROGRAM): main.c http.a
	$(CC) $(CFLAGS) $(LIBS) -o $@ $^

http.a:
	$(CC) -c $(CFLAGS) $(LIBS) -o $@ http.c


httpm1.a: http.c
	$(CC) -c $(MAC_FLAGS) $(LIBS) -o $@ $<

m1: main.c httpm1.a
	$(CC) -c $(MAC_FLAGS) $(LIBS) -o $(PROGRAM) $^


httpmacintel.a: http.c
	$(CC) -c $(MAC_FLAGS) -mmacosx-version-min=10.15 -arch x86_64 $(LIBS) -o $@ $<

macintel: main.c httpmacintel.a
	$(CC) -c $(MAC_FLAGS) -mmacosx-version-min=10.15 -arch x86_64  $(LIBS) -o $(PROGRAM) $^


.PHONY: macintel m1
