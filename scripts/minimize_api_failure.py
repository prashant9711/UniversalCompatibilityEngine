import ctypes
from ctypes import wintypes

from minimize import ddmin

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

api = kernel32.GetFileAttributesW
api.argtypes = [wintypes.LPCWSTR]
api.restype = wintypes.DWORD

INVALID_ATTRIBUTES = 0xFFFFFFFF
ERROR_INVALID_NAME = 123


def get_result(path):
    ctypes.set_last_error(0)
    attributes = api(path)

    if attributes == INVALID_ATTRIBUTES:
        return {
            "success": False,
            "error_code": ctypes.get_last_error(),
        }

    return {
        "success": True,
        "attributes": attributes,
    }


def reproduces(path):
    result = get_result(path)
    return (
        not result["success"]
        and result["error_code"] == ERROR_INVALID_NAME
    )


def main():
    original = "C:\\Windows\\invalid<>filename.txt"

    print("Original:", original)
    print("Original result:", get_result(original))

    minimized = ddmin(original, reproduces)

    print("Minimized:", repr(minimized))
    print("Minimized result:", get_result(minimized))
    print("Error preserved:", reproduces(minimized))


if __name__ == "__main__":
    main()