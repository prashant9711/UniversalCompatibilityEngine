#include <windows.h>
#include <stdio.h>
#include "../repairs/case_rename.h"

int wmain(int argc, wchar_t *argv[])
{
    if (argc != 2) {
        fprintf(stderr, "Usage: test_uce_rename.exe <directory>\n");
        return 1;
    }

    wchar_t original[MAX_PATH];
    wchar_t target[MAX_PATH];

    if (swprintf(original, MAX_PATH, L"%ls\\TestFile.txt", argv[1]) < 0 ||
        swprintf(target, MAX_PATH, L"%ls\\testfile.txt", argv[1]) < 0) {
        fprintf(stderr, "Path too long\n");
        return 1;
    }

    HANDLE file = CreateFileW(
        original,
        GENERIC_WRITE,
        FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
        NULL,
        CREATE_NEW,
        FILE_ATTRIBUTE_NORMAL,
        NULL
    );

    if (file == INVALID_HANDLE_VALUE) {
        printf("{\"create_success\":false,\"error\":%lu}\n",
               (unsigned long)GetLastError());
        return 1;
    }

    CloseHandle(file);

    BOOL renamed = UCE_MoveFileW(original, target);
    DWORD rename_error = renamed ? 0 : GetLastError();

    WIN32_FIND_DATAW data;
    HANDLE search = FindFirstFileW(target, &data);

    if (search == INVALID_HANDLE_VALUE) {
        printf(
            "{\"rename_success\":%s,\"rename_error\":%lu,"
            "\"query_success\":false}\n",
            renamed ? "true" : "false",
            (unsigned long)rename_error
        );
        return 1;
    }

    printf(
        "{\"rename_success\":%s,\"rename_error\":%lu,"
        "\"query_success\":true,\"actual_name\":\"%ls\"}\n",
        renamed ? "true" : "false",
        (unsigned long)rename_error,
        data.cFileName
    );

    FindClose(search);
    return renamed ? 0 : 1;
}