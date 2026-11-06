#ifndef UCE_CASE_RENAME_H
#define UCE_CASE_RENAME_H

#include <windows.h>

BOOL UCE_MoveFileW(
    LPCWSTR existing_path,
    LPCWSTR new_path
);

unsigned long UCE_GetMoveFileCallCount(void);

#endif