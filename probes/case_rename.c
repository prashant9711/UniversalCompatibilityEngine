#include <windows.h>
#include <stdio.h>

int wmain(int argc, wchar_t *argv[])
{
    if (argc != 2) {
        fprintf(stderr, "Usage: case_rename.exe <directory>\n");
        return 1;
    }

    wchar_t original[MAX_PATH];
    wchar_t renamed[MAX_PATH];

    swprintf(original, MAX_PATH, L"%ls\\TestFile.txt", argv[1]);
    swprintf(renamed, MAX_PATH, L"%ls\\testfile.txt", argv[1]);

    HANDLE file = CreateFileW(
        original,
        GENERIC_WRITE,
        FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
        NULL,
        CREATE_ALWAYS,
        FILE_ATTRIBUTE_NORMAL,
        NULL
    );

    if (file == INVALID_HANDLE_VALUE) {
        printf("{\"create_success\":false,\"error\":%lu}\n",
               (unsigned long)GetLastError());
        return 0;
    }

    CloseHandle(file);

    SetLastError(0);

    BOOL moved = MoveFileW(original, renamed);
    DWORD move_error = moved ? 0 : GetLastError();

    DWORD original_attrs = GetFileAttributesW(original);
    DWORD renamed_attrs = GetFileAttributesW(renamed);

    printf(
        "{\"create_success\":true,"
        "\"rename_success\":%s,"
        "\"rename_error\":%lu,"
        "\"original_exists\":%s,"
        "\"renamed_exists\":%s}\n",
        moved ? "true" : "false",
        (unsigned long)move_error,
        original_attrs != INVALID_FILE_ATTRIBUTES ? "true" : "false",
        renamed_attrs != INVALID_FILE_ATTRIBUTES ? "true" : "false"
    );

    // Preserve the file for filesystem inspection.
    return 0;
}