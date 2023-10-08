TOOLCHAIN_VER=$(shell ls /usr/lib/gcc/arm-none-eabi/ | head -n1)
LIBPATHS=-L/usr/lib/arm-none-eabi/newlib/arm/v5te/softfp \
		 -L/usr/lib/gcc/arm-none-eabi/$(TOOLCHAIN_VER)/arm/v5te/softfp

LDFLAGS= $(LIBPATHS) -lc -lnosys -lgcc
SANITIZERS=-fstack-protector-all \
           -fstack-check \
		   -fsanitize=undefined \
		   -fsanitize-undefined-trap-on-error \
		   -fsanitize-coverage=trace-pc
CFLAGS=-Os -I. -IcoreJSON/source/include -mcpu=arm926ej-s -std=c11
ARMGNU=arm-none-eabi
CC=$(ARMGNU)-gcc

all: example.bin example_unsanitary.bin

lifecycle.o: lifecycle.s
	$(ARMGNU)-as $^ -o $@

platform.o: platform.c
	$(ARMGNU)-gcc $(CFLAGS) -c $^ -o $@

example.o: example.c
	$(ARMGNU)-gcc $(CFLAGS) $(SANITIZERS) -c $^ -o $@

core_json.o: coreJSON/source/core_json.c
	$(ARMGNU)-gcc $(CFLAGS) $(SANITIZERS) -c $^ -o $@

example.elf: memmap lifecycle.o example.o core_json.o platform.o
	$(ARMGNU)-ld  -o $@ -T memmap lifecycle.o example.o core_json.o platform.o $(LDFLAGS)

example.bin: example.elf
	$(ARMGNU)-objcopy $^ $@ -O binary

example_unsanitary.o: example.c
	$(ARMGNU)-gcc $(CFLAGS) -c $^ -o $@

core_json_unsanitary.o: coreJSON/source/core_json.c
	$(ARMGNU)-gcc $(CFLAGS) -c $^ -o $@

example_unsanitary.elf: memmap lifecycle.o example_unsanitary.o core_json_unsanitary.o platform.o
	$(ARMGNU)-ld  -o $@ -T memmap lifecycle.o example_unsanitary.o core_json_unsanitary.o platform.o $(LDFLAGS)

example_unsanitary.bin: example_unsanitary.elf
	$(ARMGNU)-objcopy $^ $@ -O binary

run:
	QEMU_AUDIO_DRV=none qemu-system-arm -M versatilepb -m 8M -nographic -semihosting -kernel example.bin

run_unsanitary:
	QEMU_AUDIO_DRV=none qemu-system-arm -M versatilepb -m 8M -nographic -semihosting -kernel example_unsanitary.bin

clean:
	rm -f *.o *.bin *.elf

.PHONY: run run_unsanitary clean all
