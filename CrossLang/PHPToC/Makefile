SWIG = swig
CC = gcc
PHP_CONFIG = php-config
CFLAGS = -fPIC -shared
INCLUDES = $(shell $(PHP_CONFIG) --includes)

all: build/command.so

build/command_wrap.c: src/command.i src/command.h
	$(SWIG) -php -outdir php -o build/command_wrap.c src/command.i

build/command.so: build/command_wrap.c src/command.c
	$(CC) $(CFLAGS) -o build/command.so build/command_wrap.c src/command.c $(INCLUDES)

clean:
	rm -f build/*.so build/*.c php/*.php
