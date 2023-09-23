#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <cJSON.h>

int main() {
    uint8_t buf[4096];
    size_t rd = fread(buf, 1, sizeof(buf) - 1, stdin);
    if(rd > 0) {
        cJSON *json = cJSON_ParseWithLength(buf, rd);
        if (json) {
            char * s = cJSON_Print(json);
            if (s) {
                printf("parsed: %s\n", s);
                free(s);
            }
        }
        cJSON_Delete(json);
    }
}