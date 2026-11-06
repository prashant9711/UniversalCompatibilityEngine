
#include <windows.h>
#include <stdio.h>
#include <wchar.h>

int wmain(int argc, wchar_t *argv[])
{
    if (argc < 2) {
        fwprintf(stderr,
            L"Usage: uce_launcher.exe <program.exe> [arguments...]\n");
        return 1;
    }

    wchar_t command[32768] = L"";
    const size_t capacity = sizeof(command) / sizeof(command[0]);

    // Build the target command line.
    // Note: This simple quoting does not yet handle all Windows
    // command-line escaping rules.
    for (int i = 1; i < argc; i++) {
        size_t required = wcslen(command) + wcslen(argv[i]) + 4;

        if (required >= capacity) {
            fwprintf(stderr, L"Command line too long\n");
            return 1;
        }

        if (i > 1)
            wcscat(command, L" ");

        wcscat(command, L"\"");
        wcscat(command, argv[i]);
        wcscat(command, L"\"");
    }

    STARTUPINFOW startup = {0};
    PROCESS_INFORMATION process = {0};

    startup.cb = sizeof(startup);

    // Start the target process suspended.
    if (!CreateProcessW(
            argv[1],
            command,
            NULL,
            NULL,
            FALSE,
            CREATE_SUSPENDED,
            NULL,
            NULL,
            &startup,
            &process)) {

        fwprintf(stderr,
            L"CreateProcessW failed: %lu\n",
            (unsigned long)GetLastError());

        return 1;
    }

    // Resume the target's primary thread.
    DWORD resume_result = ResumeThread(process.hThread);

    if (resume_result == (DWORD)-1) {
        fwprintf(stderr,
            L"ResumeThread failed: %lu\n",
            (unsigned long)GetLastError());

        TerminateProcess(process.hProcess, 1);

        CloseHandle(process.hThread);
        CloseHandle(process.hProcess);

        return 1;
    }

    // Wait until the target application exits.
    DWORD wait_result =
        WaitForSingleObject(process.hProcess, INFINITE);

    if (wait_result != WAIT_OBJECT_0) {
        fwprintf(stderr,
            L"WaitForSingleObject failed: %lu\n",
            (unsigned long)GetLastError());

        CloseHandle(process.hThread);
        CloseHandle(process.hProcess);

        return 1;
    }

    DWORD exit_code = 1;

    if (!GetExitCodeProcess(process.hProcess, &exit_code)) {
        fwprintf(stderr,
            L"GetExitCodeProcess failed: %lu\n",
            (unsigned long)GetLastError());

        CloseHandle(process.hThread);
        CloseHandle(process.hProcess);

        return 1;
    }

    CloseHandle(process.hThread);
    CloseHandle(process.hProcess);

    return (int)exit_code;
}
