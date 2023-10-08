CFLAGS=-O2 -IcJSON -std=c11

SANITIZERS=-fstack-protector-all \
           -fstack-check \
		   -fsanitize=undefined \
		   -fsanitize=address

all: example-gcov example example-arm example-gcc-instr

example-gcov: example.c cJSON/cJSON.c
	gcc -ftest-coverage -fprofile-arcs $(CFLAGS) $^ -o $@

example: example.c cJSON/cJSON.c
	gcc $(CFLAGS) $^ -o $@

instrumentation.o: instrumentation.c
	gcc $(CFLAGS) $(SANITIZERS) -c $^ -o $@

example-gcc-instr: example.c cJSON/cJSON.c instrumentation.o
	gcc $(CFLAGS) $(SANITIZERS) -fsanitize-coverage=trace-pc -no-pie $^ -o $@

example-arm:
	make -C arm

clean:
	rm -f example-gcc-instr example-gcov example *.gcda *.gcno *.o
	make -C arm clean
