CFLAGS=-O2 -IcJSON -std=c11

all: example-gcov example example-arm

example-gcov: example.c cJSON/cJSON.c
	gcc -ftest-coverage -fprofile-arcs $(CFLAGS) $^ -o $@

example: example.c cJSON/cJSON.c
	gcc $(CFLAGS) $^ -o $@

example-arm:
	make -C arm

clean:
	rm -f example-gcov example *.gcda *.gcno
	make -C arm clean
