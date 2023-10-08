#include <stdio.h>

void __sanitizer_cov_trace_pc(void) {
    void * ret = __builtin_return_address(0);
    fwrite(ret, sizeof(ret), 1, stderr);
}
