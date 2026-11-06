#include <windows.h>
#include <stdio.h>
#include <wchar.h>

int wmain(int argc, wchar_t *argv[])
{
    if (argc != 2) {
        fprintf(stderr, "Usage: query_filename.exe <path>\n");
        return 1;
    }

    WIN32_FIND_DATAW data;

    HANDLE search = FindFirstFileW(argv[1], &data);

    if (search == INVALID_HANDLE_VALUE) {
        printf("{\"success\":false,\"error\":%lu}\n",
               (unsigned long)GetLastError());
        return 0;
    }

    printf("{\"success\":true,\"actual_name\":\"%ls\"}\n",
           data.cFileName);

    FindClose(search);
    return 0;
}