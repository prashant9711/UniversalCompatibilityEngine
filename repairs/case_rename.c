#include "case_rename.h"
#include <stdio.h>
#include <wchar.h>


static unsigned long uce_movefile_calls = 0;

unsigned long UCE_GetMoveFileCallCount(void)
{
    return uce_movefile_calls;
}

typedef BOOL (WINAPI *MoveFileWFn)(LPCWSTR, LPCWSTR);

static BOOL UCE_CallOriginalMoveFileW(
    LPCWSTR existing_path,
    LPCWSTR new_path
)
{
    HMODULE kernel32 = GetModuleHandleW(L"kernel32.dll");

    if (!kernel32)
        return FALSE;

    MoveFileWFn original = (MoveFileWFn)(void *)
        GetProcAddress(kernel32, "MoveFileW");

    if (!original)
        return FALSE;

    return original(existing_path, new_path);
}

static BOOL casing_matches(LPCWSTR path)
{
    WIN32_FIND_DATAW data;
    HANDLE search = FindFirstFileW(path, &data);

    if (search == INVALID_HANDLE_VALUE)
        return FALSE;

    const wchar_t *slash = wcsrchr(path, L'\\');
    const wchar_t *expected = slash ? slash + 1 : path;

    BOOL matches = wcscmp(data.cFileName, expected) == 0;
    FindClose(search);

    return matches;
}

BOOL UCE_MoveFileW(LPCWSTR existing_path, LPCWSTR new_path)
{
    uce_movefile_calls++;
    if (!existing_path || !new_path) {
        SetLastError(ERROR_INVALID_PARAMETER);
        return FALSE;
    }

    // Preserve ordinary Windows API behavior.
    if (!UCE_CallOriginalMoveFileW(existing_path, new_path))
        return FALSE;

    // No repair needed for ordinary renames.
    if (wcscmp(existing_path, new_path) == 0 ||
        _wcsicmp(existing_path, new_path) != 0)
        return TRUE;

    if (casing_matches(new_path))
        return TRUE;

    // Extract the destination directory.
    wchar_t directory[MAX_PATH];
    wcsncpy(directory, new_path, MAX_PATH - 1);
    directory[MAX_PATH - 1] = L'\0';

    wchar_t *slash = wcsrchr(directory, L'\\');
    if (!slash) {
        SetLastError(ERROR_INVALID_PARAMETER);
        return FALSE;
    }

    *slash = L'\0';

    wchar_t temporary[MAX_PATH];
    BOOL moved_to_temp = FALSE;

    for (unsigned int attempt = 0; attempt < 100; attempt++) {
        int written = swprintf(
            temporary,
            MAX_PATH,
            L"%ls\\uce_%lu_%u.tmp",
            directory,
            (unsigned long)GetCurrentProcessId(),
            attempt
        );

        if (written < 0 || written >= MAX_PATH) {
            SetLastError(ERROR_FILENAME_EXCED_RANGE);
            return FALSE;
        }

        if (UCE_CallOriginalMoveFileW(new_path, temporary)) {
            moved_to_temp = TRUE;
            break;
        }

        DWORD error = GetLastError();

        if (error != ERROR_ALREADY_EXISTS &&
            error != ERROR_FILE_EXISTS)
            return FALSE;
    }

    if (!moved_to_temp) {
        SetLastError(ERROR_ALREADY_EXISTS);
        return FALSE;
    }

    BOOL final_rename_success;

    #ifdef UCE_ENABLE_FAULT_INJECTION
        if (GetEnvironmentVariableW(
                L"UCE_TEST_FAIL_FINAL_RENAME", NULL, 0) > 0) {
            SetLastError(ERROR_ACCESS_DENIED);
            final_rename_success = FALSE;
        } else
    #endif
        {
            final_rename_success = UCE_CallOriginalMoveFileW(temporary, new_path);
        }

    if (!final_rename_success) {
        DWORD error = GetLastError();

        // Attempt to restore the original filename.
        BOOL rollback_success = UCE_CallOriginalMoveFileW(temporary, existing_path);

        if (!rollback_success) {
            DWORD rollback_error = GetLastError();

            fprintf(
                stderr,
                "Rollback failed: error %lu\n",
                (unsigned long)rollback_error
            );
        }

        // Preserve the original failure code.
        SetLastError(error);
        return FALSE;
    }

    return TRUE;
}