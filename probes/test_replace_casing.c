#include <windows.h>
#include <stdio.h>
#include <wchar.h>

int wmain(int argc, wchar_t **argv)
{
    if (argc != 2 && argc != 3) return 2;

    const wchar_t *destination_name = L"TARGET.txt";

    if (argc == 3)
    {
        if (wcscmp(argv[2], L"matching") == 0)
            destination_name = L"target.txt";
        else if (wcscmp(argv[2], L"different") != 0)
            return 2;
    }

    wchar_t source[MAX_PATH], destination[MAX_PATH], requested[MAX_PATH];
    swprintf(source, MAX_PATH, L"%ls\\source.txt", argv[1]);
    swprintf(destination, MAX_PATH, L"%ls\\%ls", argv[1], destination_name);
    swprintf(requested, MAX_PATH, L"%ls\\target.txt", argv[1]);

    HANDLE file = CreateFileW(source, GENERIC_WRITE, 0, NULL,
                              CREATE_NEW, FILE_ATTRIBUTE_NORMAL, NULL);
    if (file == INVALID_HANDLE_VALUE) return 3;
    const char source_data[] = "SOURCE_DATA_123";
    DWORD written;
    if (!WriteFile(file, source_data, sizeof(source_data) - 1,
                   &written, NULL) ||
        written != sizeof(source_data) - 1) return 5;
    CloseHandle(file);

    file = CreateFileW(destination, GENERIC_WRITE, 0, NULL,
                       CREATE_NEW, FILE_ATTRIBUTE_NORMAL, NULL);
    if (file == INVALID_HANDLE_VALUE) return 4;
    const char destination_data[] = "OLD_DESTINATION";
    if (!WriteFile(file, destination_data, sizeof(destination_data) - 1,
                   &written, NULL) ||
        written != sizeof(destination_data) - 1) return 6;
    CloseHandle(file);

    BOOL success = MoveFileExW(source, requested, MOVEFILE_REPLACE_EXISTING);
    DWORD error = success ? 0 : GetLastError();

    WIN32_FIND_DATAW data;
    HANDLE search = FindFirstFileW(requested, &data);

    if (search == INVALID_HANDLE_VALUE) {
        printf("{\"rename_success\":%s,\"error\":%lu,\"actual_name\":null}\n",
               success ? "true" : "false", (unsigned long)error);
        return 1;
    }

    printf("{\"rename_success\":%s,\"error\":%lu,\"actual_name\":\"%ls\"}\n",
           success ? "true" : "false",
           (unsigned long)error,
           data.cFileName);

    FindClose(search);
    return success ? 0 : 1;
}
