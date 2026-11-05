import ctypes
from ctypes import wintypes

from minimize import ddmin

INVALID_ATTRIBUTES = 0xFFFFFFFF

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
api = kernel32.GetFileAttributesW
api.argtypes = [wintypes.LPCWSTR]
api.restype = wintypes.DWORD


class WindowsOracle:
    def evaluate(self, path):
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


class SimulatedOracle:
    """
    Deliberately incorrect implementation for testing.
    Not an actual compatibility layer.
    """

    def __init__(self, reference):
        self.reference = reference

    def evaluate(self, path):
        result = self.reference.evaluate(path).copy()

        if not result["success"] and result["error_code"] == 123:
            result["error_code"] = 2

        return result


def is_mismatch(reference, target, path):
    return reference.evaluate(path) != target.evaluate(path)


def main():
    reference = WindowsOracle()
    target = SimulatedOracle(reference)

    original = r"C:\Windows\invalid<>filename.txt"

    print("Original mismatch:", is_mismatch(reference, target, original))

    minimized = ddmin(
        original,
        lambda path: is_mismatch(reference, target, path),
    )

    print("Minimized input:", repr(minimized))
    print("Windows result:", reference.evaluate(minimized))
    print("Target result:", target.evaluate(minimized))
    print("Mismatch preserved:", is_mismatch(reference, target, minimized))


if __name__ == "__main__":
    main()