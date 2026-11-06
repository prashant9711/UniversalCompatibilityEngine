#include <windows.h>
#include <stdio.h>
#include <wchar.h>

typedef BOOL (*InitializeFn)(void);

int wmain(int argc, wchar_t *argv[])
{
    if (argc != 3) {
        fprintf(stderr,
            "Usage: test_dll_hook.exe <directory> <dll_path>\n");
        return 1;
    }

    wchar_t original[MAX_PATH];
    wchar_t target[MAX_PATH];

    int n1 = swprintf(
        original, MAX_PATH, L"%ls\\DllTest.TXT", argv[1]
    );
    int n2 = swprintf(
        target, MAX_PATH, L"%ls\\dlltest.txt", argv[1]
    );

    if (n1 < 0 || n1 >= MAX_PATH ||
        n2 < 0 || n2 >= MAX_PATH) {
        fprintf(stderr, "Path too long\n");
        return 1;
    }

    HANDLE file = CreateFileW(
        original, GENERIC_WRITE,
        FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
        NULL, CREATE_NEW, FILE_ATTRIBUTE_NORMAL, NULL
    );

    if (file == INVALID_HANDLE_VALUE) {
        fprintf(stderr, "CreateFileW failed: %lu\n",
                (unsigned long)GetLastError());
        return 1;
    }

    CloseHandle(file);

    HMODULE dll = LoadLibraryW(argv[2]);

    if (!dll) {
        fprintf(stderr, "LoadLibraryW failed: %lu\n",
                (unsigned long)GetLastError());
        return 1;
    }

    InitializeFn initialize =
        (InitializeFn)(void *)GetProcAddress(dll, "UCE_Initialize");

    if (!initialize || !initialize()) {
        fprintf(stderr, "DLL hook initialization failed\n");
        return 1;
    }

    if (!initialize()) {
        fprintf(stderr, "Second hook initialization failed\n");
        return 1;
    }

    // Ordinary Windows API call; no direct repair invocation.
    BOOL renamed = MoveFileW(original, target);
    DWORD error = renamed ? 0 : GetLastError();

    WIN32_FIND_DATAW data;
    HANDLE search = FindFirstFileW(target, &data);

    if (search == INVALID_HANDLE_VALUE) {
        printf(
            "{\"hook_loaded\":true,\"rename_success\":%s,"
            "\"error\":%lu,\"query_success\":false}\n",
            renamed ? "true" : "false",
            (unsigned long)error
        );
        return 1;
    }

    printf(
        "{\"hook_loaded\":true,\"rename_success\":%s,"
        "\"error\":%lu,\"actual_name\":\"%ls\"}\n",
        renamed ? "true" : "false",
        (unsigned long)error,
        data.cFileName
    );

    FindClose(search);
    return renamed ? 0 : 1;
}