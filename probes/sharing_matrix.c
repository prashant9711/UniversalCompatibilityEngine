#include <windows.h>
#include <stdio.h>
#include <stdlib.h>

int wmain(int argc, wchar_t *argv[])
{
    if (argc != 6) {
        fprintf(stderr,
            "Usage: sharing_matrix.exe <path> <access1> <share1> <access2> <share2>\n");
        return 1;
    }

    DWORD access1 = wcstoul(argv[2], NULL, 0);
    DWORD share1  = wcstoul(argv[3], NULL, 0);
    DWORD access2 = wcstoul(argv[4], NULL, 0);
    DWORD share2  = wcstoul(argv[5], NULL, 0);

    SetLastError(0);

    HANDLE first = CreateFileW(
        argv[1], access1, share1, NULL,
        OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL
    );

    if (first == INVALID_HANDLE_VALUE) {
        printf("{\"first_success\":false,\"first_error\":%lu}\n",
               (unsigned long)GetLastError());
        return 0;
    }

    SetLastError(0);

    HANDLE second = CreateFileW(
        argv[1], access2, share2, NULL,
        OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL
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