import difflib


def generate_diff(old_code: str, new_code: str, file_path: str):
    old_lines = old_code.splitlines(keepends=True)
    new_lines = new_code.splitlines(keepends=True)

    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=f"{file_path} (OLD)",
        tofile=f"{file_path} (NEW)"
    )

    return "".join(diff)
