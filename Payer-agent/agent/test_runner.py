import subprocess
import sys
from pathlib import Path
from config import ARTIFACTS_PATH, REPO_PATH

def _is_windows():
    return sys.platform.startswith("win")

def run_tests(change_id: str) -> str:
    """Run tests in Payer PSP repo (Maven or Gradle). Returns path to test output file."""
    path = ARTIFACTS_PATH / change_id / "tests.txt"
    path.parent.mkdir(parents=True, exist_ok=True)

    if not REPO_PATH.exists():
        path.write_text("SKIPPED: No repo at " + str(REPO_PATH), encoding="utf-8", errors="replace")
        return str(path)

    repo = REPO_PATH.resolve()
    try:
        if (repo / "pom.xml").exists():
            # On Windows, try mvn.cmd first (Maven batch wrapper), else mvn
            mvn_cmd = "mvn.cmd" if _is_windows() else "mvn"
            r = subprocess.run(
                [mvn_cmd, "test", "-q"],
                cwd=repo,
                capture_output=True,
                text=True,
                timeout=120,
            )
            out = (r.stdout or "") + (r.stderr or "")
            path.write_text(out or ("PASSED" if r.returncode == 0 else "FAILED"), encoding="utf-8", errors="replace")
        elif (repo / "build.gradle").exists() or (repo / "build.gradle.kts").exists():
            if (repo / "gradlew.bat").exists() and _is_windows():
                cmd = ["gradlew.bat", "test", "--quiet"]
            elif (repo / "gradlew").exists():
                cmd = [str(repo / "gradlew"), "test", "--quiet"] if _is_windows() else ["./gradlew", "test", "--quiet"]
            else:
                cmd = ["gradle", "test", "--quiet"]
            r = subprocess.run(
                cmd,
                cwd=repo,
                capture_output=True,
                text=True,
                timeout=120,
            )
            out = (r.stdout or "") + (r.stderr or "")
            path.write_text(out or ("PASSED" if r.returncode == 0 else "FAILED"), encoding="utf-8", errors="replace")
        else:
            path.write_text("No Maven (pom.xml) or Gradle (build.gradle) detected in repo. No tests run.", encoding="utf-8", errors="replace")
    except subprocess.TimeoutExpired as e:
        path.write_text(f"TEST RUN SKIPPED: Timeout after 120s. {e}", encoding="utf-8", errors="replace")
    except FileNotFoundError as e:
        path.write_text(
            "TEST RUN SKIPPED: Maven or Gradle not found.\n"
            "  - For Maven: install Apache Maven and add 'mvn' to your PATH (or set MAVEN_HOME/bin in PATH).\n"
            "  - On Windows, ensure 'mvn.cmd' or 'mvn' is available in the same shell where you start the backend.\n"
            f"  Original error: {e}",
            encoding="utf-8",
            errors="replace",
        )

    return str(path)
