#include <windows.h>
#include <stdio.h>

int wmain(int argc, wchar_t *argv[])
{
    if (argc != 2) {
        fprintf(stderr, "Usage: case_rename_repair.exe <directory>\n");
        return 1;
    }

    wchar_t original[MAX_PATH];
    wchar_t temporary[MAX_PATH];
    wchar_t target[MAX_PATH];

    swprintf(original, MAX_PATH, L"%ls\\TestFile.txt", argv[1]);
    if (GetTempFileNameW(argv[1], L"ucr", 0, temporary) == 0) {
        printf(
            "{\"create_success\":true,\"repair_success\":false,"
            "\"stage\":0,\"error\":%lu}\n",
            (unsigned long)GetLastError()
        );
        return 0;
    }

    DeleteFileW(temporary);
    swprintf(target, MAX_PATH, L"%ls\\testfile.txt", argv[1]);

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
        return 0;
    }

    CloseHandle(file);

    if (!MoveFileW(original, temporary)) {
        printf("{\"create_success\":true,\"repair_success\":false,"
               "\"stage\":1,\"error\":%lu}\n",
               (unsigned long)GetLastError());
        return 0;
    }

    if (!MoveFileW(temporary, target)) {
        printf("{\"create_success\":true,\"repair_success\":false,"
               "\"stage\":2,\"error\":%lu}\n",
               (unsigned long)GetLastError());
        return 0;
    }

    WIN32_FIND_DATAW data;
    HANDLE search = FindFirstFileW(target, &data);

    if (search == INVALID_HANDLE_VALUE) {
        printf("{\"create_success\":true,\"repair_success\":false,"
               "\"stage\":3,\"error\":%lu}\n",
               (unsigned long)GetLastError());
        return 0;
    }

    printf(
        "{\"create_success\":true,"
        "\"repair_success\":true,"
        "\"actual_name\":\"%ls\"}\n",
        data.cFileName
    );

    FindClose(search);
    return 0;
}