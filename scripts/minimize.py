import sys


def ddmin(value, reproduces):
    """
    Minimize a string while preserving a reproducible condition.
    Uses delta debugging.
    """
    if not reproduces(value):
        raise ValueError("Original input does not reproduce the failure")

    current = value
    granularity = 2

    while len(current) >= 2:
        chunk_size = (len(current) + granularity - 1) // granularity
        reduced = False

        for start in range(0, len(current), chunk_size):
            candidate = current[:start] + current[start + chunk_size:]

            if reproduces(candidate):
                current = candidate
                granularity = max(2, granularity - 1)
                reduced = True
                break

        if reduced:
            continue

        if granularity >= len(current):
            break

        granularity = min(len(current), granularity * 2)

    return current


def main():
    original = "folder/nested/very_long_filename_invalid<>.txt"

    # Simulated incompatibility: triggered by "<>"
    def simulated_mismatch(value):
        return "<>" in value

    minimized = ddmin(original, simulated_mismatch)

    print(f"Original:  {original}")
    print(f"Minimized: {minimized}")
    print(f"Preserved mismatch: {simulated_mismatch(minimized)}")


if __name__ == "__main__":
    main()