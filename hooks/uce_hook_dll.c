#include <windows.h>
#include "iat_hook.h"

__declspec(dllexport)
BOOL UCE_Initialize(void)
{
    return UCE_InstallMoveFileHook();
}

BOOL WINAPI DllMain(
    HINSTANCE instance,
    DWORD reason,
    LPVOID reserved
)
{
    (void)instance;
    (void)reason;
    (void)reserved;

    return TRUE;
}