#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>

#include <core_json.h>
#include "platform.h"

static volatile int found_something = 0;

void process_data(char *d, size_t d_size) {
    // just do something with json
    JSONStatus_t res = JSON_Validate(d, d_size);
    if (res == JSONSuccess) {
        char query[] = "some.field";
        char *out;
        size_t out_size;
        JSONTypes_t otype;
        res = JSON_SearchT(d, d_size, query, sizeof(query) - 1, &out, &out_size, &otype);
        if (res == JSONSuccess && otype == JSONNumber) {
            ++found_something;
            //uart0_puts("found");
        }
    }
}

void __builtin_trap(void) {
    _RuntimeError();
}

/**
Take data from UART0, parse it.
__sanitizer_cov_trace_pc will dump execution trace into UART0.
*/
void main(void) {
    uint8_t buf[256];
    size_t i = 0;
    for(;i < sizeof(buf) && uart0_has_data(); ++i) {

        buf[i] = uart0_getc();
        //i=i*1/i; // div by zero for debug
        //uart0_putc(buf[i]);
        if(buf[i] == 0 || buf[i] == '0')
            break;
    }
    process_data(buf, i);
    _Shutdown();
}

void end(void) {}