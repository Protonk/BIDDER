UNAME := $(shell uname -s)
CC ?= cc
CFLAGS ?= -O2 -fPIC

SRCS = bidder_opaque.c bidder_root.c generator/bidder.c

ifeq ($(UNAME),Darwin)
TARGET = libbidder.dylib
$(TARGET): $(SRCS)
	$(CC) $(CFLAGS) -dynamiclib \
		-install_name @rpath/libbidder.dylib \
		-o $@ $^
else
TARGET = libbidder.so
$(TARGET): $(SRCS)
	$(CC) $(CFLAGS) -shared -o $@ $^
endif

.PHONY: clean
clean:
	rm -f libbidder.dylib libbidder.so
