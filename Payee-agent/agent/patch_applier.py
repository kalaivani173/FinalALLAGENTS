"""
Apply a unified diff to a local directory without using git.
Parses the diff and applies hunks to files under repo_path.
"""
import re
from pathlib import Path
from typing import List, Tuple


def _normalize_path(path: str) -> str:
    """Strip a/ or b/ prefix and leading slashes."""
    path = path.strip()
    for prefix in ("a/", "b/", "a\\", "b\\"):
        if path.startswith(prefix):
            path = path[len(prefix) :]
    return path.lstrip("/\\")


def _parse_unified_diff(diff_text: str) -> List[Tuple[str, List[Tuple[int, int, List[str]]]]]:
    """
    Parse unified diff into (relative_file_path, hunks).
    Each hunk is (old_start, old_count, lines) where lines are "+..." or "-..." or " ...".
    Returns list of (file_path, [hunk, ...]).
    """
    files = []
    current_file = None
    current_hunks = None
    last_old_start, last_old_count = 0, 0
    current_lines = []

    for raw_line in diff_text.splitlines():
        if raw_line.startswith("--- "):
            if current_hunks is not None and current_lines:
                current_hunks.append((last_old_start, last_old_count, current_lines))
            current_file = None
            current_hunks = None
            current_lines = []
        elif raw_line.startswith("+++ "):
            if current_hunks is not None and current_lines:
                current_hunks.append((last_old_start, last_old_count, current_lines))
            path = raw_line[4:].split("\t")[0].strip()
            current_file = _normalize_path(path)
            current_hunks = []
            current_lines = []
            files.append((current_file, current_hunks))
        elif raw_line.startswith("@@ "):
            if current_hunks is not None and current_lines:
                current_hunks.append((last_old_start, last_old_count, current_lines))
            m = re.match(r"@@ \-(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", raw_line)
            if m:
                last_old_start = int(m.group(1))
                last_old_count = int(m.group(2) or 1)
            current_lines = []
        elif current_hunks is not None and raw_line.startswith((" ", "-", "+")):
            current_lines.append(raw_line)

    if current_hunks is not None and current_lines:
        current_hunks.append((last_old_start, last_old_count, current_lines))

    return files


def _apply_hunks(original_lines: List[str], hunks: List[Tuple[int, int, List[str]]]) -> str:
    """Apply hunks to original file lines. Returns new file content (with trailing newline)."""
    result = list(original_lines)
    for old_start, old_count, hunk_lines in sorted(hunks, key=lambda h: -h[0]):
        old_idx = old_start - 1
        new_lines = []
        for hunk_line in hunk_lines:
            if hunk_line.startswith(" "):
                if 0 <= old_idx < len(result):
                    new_lines.append(result[old_idx])
                old_idx += 1
            elif hunk_line.startswith("-"):
                old_idx += 1
            elif hunk_line.startswith("+"):
                new_lines.append(hunk_line[1:].rstrip("\n\r"))
        end = min(old_start - 1 + old_count, len(result))
        result[old_start - 1 : end] = new_lines
    return "\n".join(result) + ("\n" if result else "")


def apply_diff_to_dir(diff_text: str, repo_path: Path) -> List[str]:
    """
    Apply a unified diff to files under repo_path.
    Returns list of modified file paths (relative to repo_path).
    Skips files that don't exist (new files: create with content from + lines only).
    """
    if not diff_text or not diff_text.strip():
        return []
    parsed = _parse_unified_diff(diff_text)
    modified = []
    repo_path = Path(repo_path).resolve()
    for rel_path, hunks in parsed:
        if not rel_path or not hunks:
            continue
        target = repo_path / rel_path
        # Build new content: for existing file apply hunks; for new file use only + lines
        if target.exists():
            try:
                original = target.read_text(encoding="utf-8")
            except Exception:
                continue
            original_lines = original.splitlines()
            new_content = _apply_hunks(original_lines, hunks)
            target.write_text(new_content, encoding="utf-8")
            modified.append(rel_path)
        else:
            # New file: take only + lines from first hunk (simple: all hunks + lines)
            new_lines = []
            for _, _, hunk_lines in hunks:
                for ln in hunk_lines:
                    if ln.startswith("+"):
                        new_lines.append(ln[1:].rstrip("\n") + "\n")
            if new_lines:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("".join(new_lines), encoding="utf-8")
                modified.append(rel_path)
    return modified
