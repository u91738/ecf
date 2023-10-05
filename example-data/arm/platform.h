#include <stdbool.h>
#include <stdint.h>

#pragma once

__attribute__((naked))
__attribute__((noreturn))
void _Shutdown(void);

__attribute__((naked))
__attribute__((noreturn))
void _RuntimeError(void);

bool uart0_has_data(void);
void uart0_putc(char c);
void uart0_puts(const char *s);
char uart0_getc(void);
