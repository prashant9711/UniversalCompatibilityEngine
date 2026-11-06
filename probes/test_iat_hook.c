#include <windows.h>
#include <stdio.h>
#include <wchar.h>
#include "../hooks/iat_hook.h"
#include "../repairs/case_rename.h"

int wmain(int argc, wchar_t *argv[])
{
    if (argc != 2) {
        fprintf(stderr, "Usage: test_iat_hook.exe <directory>\n");
        return 1;
    }

    wchar_t original[MAX_PATH];
    wchar_t target[MAX_PATH];

    int n1 = swprintf(
        original, MAX_PATH, L"%ls\\HookTest.TXT", argv[1]
    );
    int n2 = swprintf(
        target, MAX_PATH, L"%ls\\hooktest.txt", argv[1]
    );

    if (n1 < 0 || n1 >= MAX_PATH ||
        n2 < 0 || n2 >= MAX_PATH) {
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
        fprintf(stderr, "CreateFileW failed: %lu\n",
                (unsigned long)GetLastError());
        return 1;
    }

    CloseHandle(file);

    BOOL hook_installed = UCE_InstallMoveFileHook();

    if (!hook_installed) {
        fprintf(stderr, "IAT hook installation failed\n");
        return 1;
    }

    // Intentionally call the normal Windows API.
    BOOL renamed = MoveFileW(original, target);
    DWORD rename_error = renamed ? 0 : GetLastError();

    WIN32_FIND_DATAW data;
    HANDLE search = FindFirstFileW(target, &data);

    if (search == INVALID_HANDLE_VALUE) {
        printf(
            "{\"hook_installed\":true,"
            "\"rename_success\":%s,"
            "\"rename_error\":%lu,"
            "\"query_success\":false}\n",
            renamed ? "true" : "false",
            (unsigned long)rename_error
        );
        return 1;
    }

    printf(
        "{\"hook_installed\":true,"
        "\"rename_success\":%s,"
        "\"rename_error\":%lu,"
        "\"actual_name\":\"%ls\","
        "\"hook_calls\":%lu}\n",
        renamed ? "true" : "false",
        (unsigned long)rename_error,
        data.cFileName,
        UCE_GetMoveFileCallCount()
    );

    FindClose(search);
    return renamed ? 0 : 1;
}