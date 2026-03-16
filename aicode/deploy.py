"""
Deploy approved code to javacoderepo. Supported only for changeType == "field-addition".
Backs up existing files with _old extension before writing new content.
Optional: commit and push to Git (see deploy_config).
"""
import json
import logging
import os
import re
import subprocess
import time
from datetime import datetime

_log = logging.getLogger(__name__)

from deploy_config import (
    get_javacoderepo_root,
    DEPLOY_GIT_ENABLED,
    DEPLOY_GIT_COMMIT_ONLY,
    DEPLOY_GIT_BRANCH,
    DEPLOY_GIT_REMOTE,
    DEPLOY_GIT_COMMIT_MESSAGE_TEMPLATE,
    DEPLOY_GIT_ALLOW_DIRTY_REPO,
    DEPLOY_GIT_ADD_TIMEOUT,
    DEPLOY_GIT_COMMIT_TIMEOUT,
    DEPLOY_GIT_PUSH_TIMEOUT,
    DEPLOY_GIT_PUSH_RETRIES,
)

# Change type allowed for deploy (only Field Addition)
DEPLOY_ALLOWED_CHANGE_TYPE = "field-addition"

# Standard segment that identifies Java source root
SRC_MAIN_JAVA = os.path.join("src", "main", "java")

# Known modules under javacoderepo (for path resolution fallback)
KNOWN_MODULES = ("UPISim", "PayerPSP", "PayeePSP", "RemitterBank", "BeneficiaryBank")

# Package regex to derive path from newCode when filePath is just a filename
PACKAGE_RE = re.compile(r"^\s*package\s+([\w.]+)\s*;", re.MULTILINE)

_DEPLOY_AUDIT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "artifacts", "deploy_audit.jsonl")


def write_deploy_audit(change_id: str, deployed_paths: list[str], git_result: dict) -> None:
    """Append one JSON line to deploy_audit.jsonl. No file contents or credentials."""
    try:
        os.makedirs(os.path.dirname(_DEPLOY_AUDIT_FILE), exist_ok=True)
        entry = {
            "changeId": change_id,
            "timestamp": datetime.utcnow().isoformat(),
            "deployedFiles": deployed_paths,
            "gitCommitPush": {
                "ok": git_result.get("ok"),
                "branch": git_result.get("branch"),
                "commitHash": git_result.get("commitHash"),
                "pushed": git_result.get("pushed"),
                "errorCode": git_result.get("errorCode"),
                "message": git_result.get("message"),
            },
        }
        with open(_DEPLOY_AUDIT_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError as e:
        _log.warning("Failed to write deploy audit: %s", e)


def resolve_target_path(file_path: str, javacoderepo_root: str, new_code: str = "") -> str | None:
    """
    Resolve CR file path (from patch, may be absolute on agent machine) to absolute path
    under javacoderepo. Returns None if resolution fails.

    - If file_path contains "src/main/java", we take the module as the parent of "src"
      and target = javacoderepo_root / module / src/main/java / rest.
    - If file_path is only a filename (e.g. ReqPay.java), derive directory from package
      in new_code and try each known module until one exists.
    """
    if not file_path or not javacoderepo_root:
        return None
    norm = os.path.normpath(file_path)
    # Normalize separators for string search
    norm_lower = norm.replace("\\", "/").lower()
    src_java = SRC_MAIN_JAVA.replace("\\", "/")
    idx = norm_lower.find(src_java)
    if idx >= 0:
        # .../ModuleName/src/main/java/com/npci/...
        before = norm[:idx].rstrip(os.sep)
        after = norm[idx + len(SRC_MAIN_JAVA) :].lstrip(os.sep)
        module = os.path.basename(before)
        if not module:
            return None
        target = os.path.join(javacoderepo_root, module, SRC_MAIN_JAVA, after)
        return os.path.normpath(target)
    # Bare filename: use package from newCode and try known modules
    if not new_code or "/" not in norm and "\\" not in norm:
        # Just a filename like ReqPay.java -> put under UPISim by default
        for mod in KNOWN_MODULES:
            cand = os.path.join(javacoderepo_root, mod, SRC_MAIN_JAVA)
            if os.path.isdir(cand):
                target = os.path.join(cand, norm)
                return os.path.normpath(target)
        return os.path.normpath(os.path.join(javacoderepo_root, "UPISim", SRC_MAIN_JAVA, norm))
    m = PACKAGE_RE.search(new_code)
    if m:
        pkg = m.group(1).strip()
        rel = pkg.replace(".", os.sep) + os.sep + os.path.basename(norm)
        for mod in KNOWN_MODULES:
            target = os.path.join(javacoderepo_root, mod, SRC_MAIN_JAVA, rel)
            if os.path.isdir(os.path.dirname(target)) or mod == "UPISim":
                return os.path.normpath(target)
    return None


def deploy_dry_run(
    files: list[dict],
    javacoderepo_root: str,
) -> tuple[list[dict], list[str]]:
    """
    Resolve target paths and return what would be deployed, without writing files or touching Git.
    Returns (would_deploy_list, errors). Each entry: { targetPath, wouldBackup }.
    """
    would_deploy = []
    errors = []
    for i, f in enumerate(files or []):
        file_path = (f.get("filePath") or f.get("file") or f.get("fileName") or "").strip()
        new_code = f.get("newCode") or ""
        if not new_code and not file_path:
            errors.append(f"File entry {i + 1}: missing filePath and newCode")
            continue
        target = resolve_target_path(file_path, javacoderepo_root, new_code)
        if not target:
            errors.append(f"Could not resolve target path for: {file_path or '(no path)'}")
            continue
        if not target.startswith(os.path.normpath(javacoderepo_root)):
            errors.append(f"Resolved path outside javacoderepo: {target}")
            continue
        would_backup = os.path.isfile(target)
        would_deploy.append({"targetPath": target, "wouldBackup": would_backup})
    return would_deploy, errors


def deploy_files(
    files: list[dict],
    javacoderepo_root: str,
) -> tuple[list[dict], list[str]]:
    """
    For each file in CR files list (each has fileName, filePath, newCode),
    resolve target path under javacoderepo, backup existing to _old, write newCode.
    Returns (deployed_list, errors_list).
    """
    deployed = []
    errors = []
    for i, f in enumerate(files or []):
        file_path = (f.get("filePath") or f.get("file") or f.get("fileName") or "").strip()
        new_code = f.get("newCode") or ""
        if not new_code and not file_path:
            errors.append(f"File entry {i + 1}: missing filePath and newCode")
            continue
        target = resolve_target_path(file_path, javacoderepo_root, new_code)
        if not target:
            errors.append(f"Could not resolve target path for: {file_path or '(no path)'}")
            continue
        if not target.startswith(os.path.normpath(javacoderepo_root)):
            errors.append(f"Resolved path outside javacoderepo: {target}")
            continue
        entry = {"targetPath": target, "backedUp": None}
        try:
            if os.path.isfile(target):
                # Backup existing file, but ensure the backup is NOT a .java source file
                # so that it is ignored by the Java compiler/build.
                backup = target + ".bak"
                os.replace(target, backup)
                entry["backedUp"] = backup
            dir_path = os.path.dirname(target)
            os.makedirs(dir_path, exist_ok=True)
            with open(target, "w", encoding="utf-8") as out:
                out.write(new_code)
            deployed.append(entry)
        except OSError as e:
            errors.append(f"{target}: {e}")
    return deployed, errors


def _run_git(cwd: str, args: list[str], timeout: int) -> tuple[int, str, str]:
    r = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return r.returncode, (r.stdout or ""), (r.stderr or "")


def git_commit_and_push(
    javacoderepo_root: str,
    change_id: str,
    deployed: list[dict],
) -> dict:
    """
    Optionally commit deployed files and push to Git.
    Returns dict: ok, message, branch?, remote?, commitHash?, pushed?, errorCode?
    """
    def ok_result(msg: str, pushed: bool = False):
        return {"ok": True, "message": msg, "pushed": pushed}

    def fail_result(msg: str, error_code: str):
        return {"ok": False, "message": msg, "errorCode": error_code, "pushed": False}

    if not DEPLOY_GIT_ENABLED:
        return {**ok_result("skipped (set DEPLOY_GIT_ENABLED=1 to enable)")}

    _log.info("Deploy Git: commit/push started for changeId=%s", change_id)

    if not deployed:
        return {**ok_result("no files to commit")}

    git_dir = os.path.join(javacoderepo_root, ".git")
    if not os.path.isdir(git_dir):
        return fail_result("javacoderepo is not a Git repository", "NOT_A_GIT_REPO")

    # Use paths relative to repo root with forward slashes for reliable git add on Windows
    def to_git_path(abs_path: str) -> str:
        rel = os.path.relpath(abs_path, javacoderepo_root)
        return rel.replace("\\", "/")

    paths_to_add = []
    for entry in deployed:
        target = entry.get("targetPath")
        if target and os.path.isfile(target):
            paths_to_add.append(to_git_path(target))
        backup = entry.get("backedUp")
        if backup and os.path.isfile(backup):
            paths_to_add.append(to_git_path(backup))
    if not paths_to_add:
        return {**ok_result("no deploy paths to add")}

    # Pre-flight: dirty repo check (uses absolute paths for comparison)
    if not DEPLOY_GIT_ALLOW_DIRTY_REPO:
        try:
            code, out, _ = _run_git(javacoderepo_root, ["status", "--porcelain"], DEPLOY_GIT_ADD_TIMEOUT)
            if code == 0 and out.strip():
                our_paths = set()
                for e in deployed:
                    t = e.get("targetPath")
                    if t and os.path.isfile(t):
                        our_paths.add(os.path.normpath(t))
                    b = e.get("backedUp")
                    if b and os.path.isfile(b):
                        our_paths.add(os.path.normpath(b))
                for line in out.splitlines():
                    s = line.strip()
                    if len(s) >= 4:
                        path_part = s[3:].strip().strip('"')
                        full = os.path.normpath(os.path.join(javacoderepo_root, path_part))
                        if full not in our_paths:
                            return fail_result(
                                "Repo has other uncommitted changes; commit or stash first, or set DEPLOY_GIT_ALLOW_DIRTY_REPO=1",
                                "REPO_DIRTY",
                            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    # Pre-flight: branch existence (if explicit branch set)
    if DEPLOY_GIT_BRANCH:
        try:
            code, _, _ = _run_git(javacoderepo_root, ["rev-parse", "--verify", DEPLOY_GIT_BRANCH], DEPLOY_GIT_ADD_TIMEOUT)
            if code != 0:
                return fail_result(f"Branch '{DEPLOY_GIT_BRANCH}' does not exist", "BRANCH_NOT_FOUND")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    branch = DEPLOY_GIT_BRANCH
    remote = DEPLOY_GIT_REMOTE or "origin"
    if not branch:
        try:
            code, out, _ = _run_git(javacoderepo_root, ["rev-parse", "--abbrev-ref", "HEAD"], DEPLOY_GIT_ADD_TIMEOUT)
            if code == 0 and out.strip():
                branch = out.strip()
            else:
                branch = "HEAD"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            branch = "HEAD"

    try:
        add_cmd = ["add"] + paths_to_add
        code, out, err = _run_git(javacoderepo_root, add_cmd, DEPLOY_GIT_ADD_TIMEOUT)
        if code != 0:
            return fail_result(f"git add failed: {err or out or 'unknown'}", "GIT_ADD_FAILED")

        msg = DEPLOY_GIT_COMMIT_MESSAGE_TEMPLATE.format(changeId=change_id, timestamp=datetime.utcnow().isoformat())
        code, out, err = _run_git(javacoderepo_root, ["commit", "-m", msg], DEPLOY_GIT_COMMIT_TIMEOUT)
        if code != 0:
            if "nothing to commit" in out or "nothing to commit" in err:
                return {**ok_result("nothing to commit (already committed)"), "branch": branch, "remote": remote}
            return fail_result(f"git commit failed: {err or out or 'unknown'}", "GIT_COMMIT_FAILED")

        code, out, _ = _run_git(javacoderepo_root, ["rev-parse", "HEAD"], DEPLOY_GIT_COMMIT_TIMEOUT)
        commit_hash = out.strip() if code == 0 and out.strip() else None

        pushed = False
        if not DEPLOY_GIT_COMMIT_ONLY:
            push_cmd = ["push", remote, branch]
            last_err = None
            for attempt in range(DEPLOY_GIT_PUSH_RETRIES + 1):
                code, out, err = _run_git(javacoderepo_root, push_cmd, DEPLOY_GIT_PUSH_TIMEOUT)
                if code == 0:
                    pushed = True
                    break
                last_err = err or out or "unknown"
                if "rejected" in last_err.lower() and "non-fast-forward" in last_err.lower():
                    break
                if attempt < DEPLOY_GIT_PUSH_RETRIES:
                    time.sleep(2)
            if not pushed:
                _log.warning("Deploy Git: push failed changeId=%s errorCode=GIT_PUSH_FAILED", change_id)
                return {
                    **fail_result(f"git push failed: {last_err}", "GIT_PUSH_FAILED"),
                    "branch": branch,
                    "remote": remote,
                    "commitHash": commit_hash,
                }

        _log.info(
            "Deploy Git: finished changeId=%s branch=%s commitHash=%s pushed=%s",
            change_id, branch, commit_hash, pushed,
        )
        return {
            "ok": True,
            "message": "committed and pushed" if pushed else "committed (no push)",
            "branch": branch,
            "remote": remote,
            "commitHash": commit_hash,
            "pushed": pushed,
        }
    except subprocess.TimeoutExpired:
        _log.warning("Deploy Git: failed changeId=%s errorCode=GIT_TIMEOUT", change_id)
        return fail_result("git command timed out", "GIT_TIMEOUT")
    except FileNotFoundError:
        _log.warning("Deploy Git: failed changeId=%s errorCode=GIT_NOT_FOUND", change_id)
        return fail_result("git not found in PATH", "GIT_NOT_FOUND")
    except Exception as e:
        _log.warning("Deploy Git: failed changeId=%s errorCode=GIT_ERROR message=%s", change_id, str(e))
        return fail_result(str(e), "GIT_ERROR")
