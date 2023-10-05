.global _Reset
_Reset:
    LDR sp, =stack_top
    BL main
    B .

.global _Shutdown
_Shutdown:
    // see https://developer.arm.com/documentation/dui0471/g/Semihosting/angel-SWIreason-ReportException--0x18-
    mov r0, #0x18
    ldr r1, =0x20026
    svc 0x00123456

.global _RuntimeError
_RuntimeError:
    mov r0, #0x18
    ldr r1, =0x20023
    svc 0x00123456
