#include <windows.h>
#include <stdio.h>
#include <wchar.h>
#include "../repairs/case_rename.h"

int wmain(int argc, wchar_t *argv[])
{
    if (argc != 4) {
        fprintf(stderr,
            "Usage: test_generic_rename.exe <directory> <original> <target>\n");
        return 1;
    }

    wchar_t original[MAX_PATH];
    wchar_t target[MAX_PATH];

    int n1 = swprintf(original, MAX_PATH, L"%ls\\%ls", argv[1], argv[2]);
    int n2 = swprintf(target, MAX_PATH, L"%ls\\%ls", argv[1], argv[3]);

    if (n1 < 0 || n1 >= MAX_PATH || n2 < 0 || n2 >= MAX_PATH) {
        fprintf(stderr, "Path too long\n");
        return 1;
    }

    HANDLE file = CreateFileW(
        original, GENERIC_WRITE,
        FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
        NULL, CREATE_NEW, FILE_ATTRIBUTE_NORMAL, NULL
    );

    if (file == INVALID_HANDLE_VALUE) {
        printf("{\"create_success\":false,\"error\":%lu}\n",
               (unsigned long)GetLastError());
        return 1;
    }

    CloseHandle(file);

    BOOL success = UCE_MoveFileW(original, target);
    DWORD error = success ? 0 : GetLastError();

    WIN32_FIND_DATAW data;
    HANDLE search = FindFirstFileW(target, &data);

    if (search == INVALID_HANDLE_VALUE) {
        printf("{\"rename_success\":%s,\"error\":%lu,\"query_success\":false}\n",
               success ? "true" : "false", (unsigned long)error);
        return 1;
    }

    printf(
        "{\"rename_success\":%s,\"error\":%lu,\"actual_name\":\"%ls\"}\n",
        success ? "true" : "false",
        (unsigned long)error,
        data.cFileName
    );

    FindClose(search);
    return success ? 0 : 1;
}