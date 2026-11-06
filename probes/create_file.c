#include <windows.h>
#include <stdio.h>

int wmain(int argc, wchar_t *argv[])
{
    if (argc != 2) {
        fprintf(stderr, "Usage: create_file.exe <path>\n");
        return 1;
    }

    SetLastError(0);

    HANDLE file = CreateFileW(
        argv[1],
        GENERIC_READ,
        FILE_SHARE_READ,
        NULL,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        NULL
    );

    if (file == INVALID_HANDLE_VALUE) {
        printf(
            "{\"success\":false,\"error_code\":%lu}\n",
            (unsigned long)GetLastError()
        );
    } else {
        printf("{\"success\":true}\n");
        CloseHandle(file);
    }

    return 0;
}