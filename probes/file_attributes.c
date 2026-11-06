#include <windows.h>
#include <stdio.h>
#include <wchar.h>

int wmain(int argc, wchar_t *argv[])
{
    if (argc != 2) {
        fprintf(stderr, "Usage: file_attributes.exe <path>\n");
        return 1;
    }

    SetLastError(0);

    DWORD attributes = GetFileAttributesW(argv[1]);

    if (attributes == INVALID_FILE_ATTRIBUTES) {
        printf(
            "{\"success\":false,\"error_code\":%lu}\n",
            (unsigned long)GetLastError()
        );
    } else {
        printf(
            "{\"success\":true,\"attributes\":%lu}\n",
            (unsigned long)attributes
        );
    }

    return 0;
}