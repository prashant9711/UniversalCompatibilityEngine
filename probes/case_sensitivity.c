#include <windows.h>
#include <stdio.h>

int wmain(int argc, wchar_t *argv[])
{
    if (argc != 2) {
        fprintf(stderr, "Usage: case_sensitivity.exe <directory>\n");
        return 1;
    }

    wchar_t original[MAX_PATH];
    wchar_t lowercase[MAX_PATH];

    swprintf(original, MAX_PATH, L"%ls\\TestFile.txt", argv[1]);
    swprintf(lowercase, MAX_PATH, L"%ls\\testfile.txt", argv[1]);

    HANDLE first = CreateFileW(
        original,
        GENERIC_WRITE,
        FILE_SHARE_READ | FILE_SHARE_WRITE,
        NULL,
        CREATE_ALWAYS,
        FILE_ATTRIBUTE_NORMAL,
        NULL
    );

    if (first == INVALID_HANDLE_VALUE) {
        printf("{\"first_success\":false,\"error\":%lu}\n",
               (unsigned long)GetLastError());
        return 0;
    }

    CloseHandle(first);

    SetLastError(0);

    HANDLE second = CreateFileW(
        lowercase,
        GENERIC_WRITE,
        FILE_SHARE_READ | FILE_SHARE_WRITE,
        NULL,
        CREATE_NEW,
        FILE_ATTRIBUTE_NORMAL,
        NULL
    );

    if (second == INVALID_HANDLE_VALUE) {
        printf(
            "{\"first_success\":true,"
            "\"second_success\":false,"
            "\"error\":%lu}\n",
            (unsigned long)GetLastError()
        );
    } else {
        printf(
            "{\"first_success\":true,"
            "\"second_success\":true}\n"
        );
        CloseHandle(second);
    }

    DeleteFileW(original);
    DeleteFileW(lowercase);

    return 0;
}