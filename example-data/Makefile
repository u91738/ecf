
# -I .... cJSON.h

CFLAGS=-O2 -IcJSON #-g

all: example-gcov example

example-gcov: example.c cJSON/cJSON.c
	gcc -ftest-coverage -fprofile-arcs $(CFLAGS) $^ -o $@

example: example.c cJSON/cJSON.c
	gcc $(CFLAGS) $^ -o $@

clean:
	rm -f example-gcov example *.gcda *.gcno