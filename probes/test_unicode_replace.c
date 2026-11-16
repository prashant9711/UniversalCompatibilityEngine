#include <windows.h>
#include <stdio.h>
#include <wchar.h>
#include <locale.h>

int wmain(int argc, wchar_t **argv)
{
    if (argc != 3) return 2;

    const wchar_t *existing;
    const wchar_t *requested_name;

    if (!wcscmp(argv[2], L"ascii"))
    {
        existing = L"TARGET.txt";
        requested_name = L"target.txt";
    }
    else if (!wcscmp(argv[2], L"accented"))
    {
        existing = L"CAF\u00c9.txt";
        requested_name = L"caf\u00e9.txt";
    }
    else if (!wcscmp(argv[2], L"greek"))
    {
        existing = L"\u0394\u039f\u039a\u0399\u039c\u0397.txt";
        requested_name = L"\u03b4\u03bf\u03ba\u03b9\u03bc\u03b7.txt";
    }
    else return 2;

    wchar_t source[MAX_PATH];
    wchar_t destination[MAX_PATH];
    wchar_t requested[MAX_PATH];

    swprintf(source, MAX_PATH, L"%ls\\source.txt", argv[1]);
    swprintf(destination, MAX_PATH, L"%ls\\%ls", argv[1], existing);
    swprintf(requested, MAX_PATH, L"%ls\\%ls", argv[1], requested_name);

    HANDLE file = CreateFileW(
        source, GENERIC_WRITE, 0, NULL,
        CREATE_NEW, FILE_ATTRIBUTE_NORMAL, NULL
    );

    if (file == INVALID_HANDLE_VALUE) return 3;

    const char source_data[] = "SOURCE_DATA_123";
    DWORD written;

    if (!WriteFile(file, source_data, sizeof(source_data) - 1,
                   &written, NULL))
    {
        CloseHandle(file);
        return 5;
    }

    CloseHandle(file);

    file = CreateFileW(
        destination, GENERIC_WRITE, 0, NULL,
        CREATE_NEW, FILE_ATTRIBUTE_NORMAL, NULL
    );

    if (file == INVALID_HANDLE_VALUE) return 4;

    const char destination_data[] = "OLD_DESTINATION";

    if (!WriteFile(file, destination_data,
                   sizeof(destination_data) - 1,
                   &written, NULL))
    {
        CloseHandle(file);
        return 6;
    }

    CloseHandle(file);

    BOOL success = MoveFileExW(
        source,
        requested,
        MOVEFILE_REPLACE_EXISTING
    );

    DWORD error = success ? 0 : GetLastError();

    WIN32_FIND_DATAW data;
    HANDLE search = FindFirstFileW(requested, &data);

    if (search == INVALID_HANDLE_VALUE)
    {
        printf("{\"rename_success\":%s,\"error\":%lu,\"actual_name\":null}\n",
               success ? "true" : "false",
               (unsigned long)error);
        return 1;
    }

    /* Print UTF-16 code units to avoid terminal encoding differences. */
    printf("{\"rename_success\":%s,\"error\":%lu,\"actual_name_utf16\":[" ,
           success ? "true" : "false",
           (unsigned long)error);

    for (unsigned int i = 0; data.cFileName[i]; i++)
        printf("%s%u", i ? "," : "", (unsigned int)data.cFileName[i]);

    printf("]}\n");

    FindClose(search);

    return success ? 0 : 1;
}
