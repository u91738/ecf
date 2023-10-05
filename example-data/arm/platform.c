#include "platform.h"

/*
 for register meanings see
 https://developer.arm.com/documentation/ddi0183/g/programmers-model/summary-of-registers?lang=en
*/
volatile uint32_t * const UART0DR = (uint32_t*)0x101f1000;
volatile uint32_t * const UART0FR = (uint32_t*)0x101f1000 + 0x18;
#define RXFE (1<<4)

bool uart0_has_data(void) {
    uint32_t fr = *UART0FR;
    return !(fr & RXFE);
}

void uart0_putc(char c) {
    *UART0DR = (uint32_t)c;
}

void uart0_puts(const char *s) {
    while(*s) {
        uart0_putc(*s);
        ++s;
    }
}

char uart0_getc(void) {
    return (char)*UART0DR;
}

static inline void uart0_put_addr(void *p) {
    uint32_t u = (uint32_t)p;
    *UART0DR = u & 0xFF;
    *UART0DR = (u & 0xFF00 ) >> 8;
    *UART0DR = (u & 0xFF0000 ) >> 16;
    *UART0DR = (u & 0xFF000000 ) >> 24;
}

void __sanitizer_cov_trace_pc(void) {
    uart0_put_addr(__builtin_return_address(0));
}
