#include <windows.h>
#include <stdio.h>

int wmain(int argc, wchar_t *argv[])
{
    if (argc != 2) {
        fprintf(stderr, "Usage: file_sharing.exe <path>\n");
        return 1;
    }

    HANDLE first = CreateFileW(
        argv[1],
        GENERIC_READ,
        0,                  // Deny all sharing
        NULL,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        NULL
    );

    if (first == INVALID_HANDLE_VALUE) {
        printf(
            "{\"first_success\":false,\"first_error\":%lu}\n",
            (unsigned long)GetLastError()
        );
        return 0;
    }

    SetLastError(0);

    HANDLE second = CreateFileW(
        argv[1],
        GENERIC_READ,
        FILE_SHARE_READ,
        NULL,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        NULL
    );

    if (second == INVALID_HANDLE_VALUE) {
        printf(
            "{\"first_success\":true,"
            "\"second_success\":false,"
            "\"second_error\":%lu}\n",
            (unsigned long)GetLastError()
        );
    } else {
        printf(
            "{\"first_success\":true,"
            "\"second_success\":true}\n"
        );
        CloseHandle(second);
    }

    CloseHandle(first);
    return 0;
}