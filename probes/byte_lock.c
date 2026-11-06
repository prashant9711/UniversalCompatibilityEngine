#include <windows.h>
#include <stdio.h>
#include <stdlib.h>

int wmain(int argc, wchar_t *argv[])
{
    if (argc != 5) {
        fprintf(stderr,
            "Usage: byte_lock.exe <path> <offset> <length> <hold_ms>\n");
        return 1;
    }

    DWORD offset = wcstoul(argv[2], NULL, 10);
    DWORD length = wcstoul(argv[3], NULL, 10);
    DWORD hold_ms = wcstoul(argv[4], NULL, 10);

    HANDLE file = CreateFileW(
        argv[1],
        GENERIC_READ | GENERIC_WRITE,
        FILE_SHARE_READ | FILE_SHARE_WRITE,
        NULL,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        NULL
    );

    if (file == INVALID_HANDLE_VALUE) {
        printf("{\"open_success\":false,\"error\":%lu}\n",
               (unsigned long)GetLastError());
        return 0;
    }

    OVERLAPPED overlap = {0};
    overlap.Offset = offset;

    SetLastError(0);

    BOOL locked = LockFileEx(
        file,
        LOCKFILE_EXCLUSIVE_LOCK | LOCKFILE_FAIL_IMMEDIATELY,
        0,
        length,
        0,
        &overlap
    );

    if (!locked) {
        printf("{\"open_success\":true,\"lock_success\":false,"
               "\"error\":%lu}\n",
               (unsigned long)GetLastError());
    } else {
        printf("{\"open_success\":true,\"lock_success\":true}\n");
        fflush(stdout);

        Sleep(hold_ms);

        UnlockFileEx(file, 0, length, 0, &overlap);
    }

    CloseHandle(file);
    return 0;
}