#include "iat_hook.h"
#include "../repairs/case_rename.h"

#include <winnt.h>
#include <string.h>

BOOL UCE_InstallMoveFileHook(void)
{
    HMODULE module = GetModuleHandleW(NULL);
    if (!module)
        return FALSE;

    BYTE *base = (BYTE *)module;

    IMAGE_DOS_HEADER *dos = (IMAGE_DOS_HEADER *)base;
    if (dos->e_magic != IMAGE_DOS_SIGNATURE)
        return FALSE;

    IMAGE_NT_HEADERS *nt =
        (IMAGE_NT_HEADERS *)(base + dos->e_lfanew);

    if (nt->Signature != IMAGE_NT_SIGNATURE)
        return FALSE;

    IMAGE_DATA_DIRECTORY imports =
        nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT];

    if (!imports.VirtualAddress)
        return FALSE;

    IMAGE_IMPORT_DESCRIPTOR *descriptor =
        (IMAGE_IMPORT_DESCRIPTOR *)(base + imports.VirtualAddress);

    for (; descriptor->Name; descriptor++) {
        const char *dll = (const char *)(base + descriptor->Name);

        if (_stricmp(dll, "KERNEL32.dll") != 0)
            continue;

        IMAGE_THUNK_DATA *original =
            (IMAGE_THUNK_DATA *)(base + descriptor->OriginalFirstThunk);

        IMAGE_THUNK_DATA *iat =
            (IMAGE_THUNK_DATA *)(base + descriptor->FirstThunk);

        for (; original->u1.AddressOfData; original++, iat++) {
            if (IMAGE_SNAP_BY_ORDINAL(original->u1.Ordinal))
                continue;

            IMAGE_IMPORT_BY_NAME *import =
                (IMAGE_IMPORT_BY_NAME *)(base + original->u1.AddressOfData);

            if (strcmp((const char *)import->Name, "MoveFileW") != 0)
                continue;

            if (iat->u1.Function == (ULONG_PTR)UCE_MoveFileW)
                return TRUE;

            DWORD old_protection;

            if (!VirtualProtect(
                    &iat->u1.Function,
                    sizeof(iat->u1.Function),
                    PAGE_READWRITE,
                    &old_protection))
                return FALSE;

            iat->u1.Function =
                (ULONG_PTR)UCE_MoveFileW;

            DWORD restored;
            VirtualProtect(
                &iat->u1.Function,
                sizeof(iat->u1.Function),
                old_protection,
                &restored
            );

            return TRUE;
        }
    }

    return FALSE;
}