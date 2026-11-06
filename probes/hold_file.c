#include <windows.h>
#include <stdio.h>

int wmain(int argc, wchar_t *argv[])
{
    if (argc != 2) {
        fprintf(stderr, "Usage: hold_file.exe <path>\n");
        return 1;
    }

    HANDLE file = CreateFileW(
        argv[1],
        GENERIC_READ,
        0,
        NULL,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        NULL
    );

    if (file == INVALID_HANDLE_VALUE) {
        printf("{\"success\":false,\"error_code\":%lu}\n",
               (unsigned long)GetLastError());
        return 1;
    }

    printf("{\"success\":true,\"holding\":true}\n");
    fflush(stdout);

    Sleep(15000);

    CloseHandle(file);
    return 0;
}