"""
Test patch_applier on local repo (no git, no LLM).
Applies a minimal unified diff to repo/PayerPSP and verifies the file changed.
Run: python test_patch_apply.py
"""
from pathlib import Path
from config import REPO_PATH
from agent.patch_applier import apply_diff_to_dir

# Minimal diff: add a comment line after "public class Txn {" in Txn.java
# Path must match repo structure: src/main/java/com/payer/PayerPSP/dto/Txn.java
SAMPLE_DIFF = r"""--- a/src/main/java/com/payer/PayerPSP/dto/Txn.java
+++ b/src/main/java/com/payer/PayerPSP/dto/Txn.java
@@ -8,6 +8,7 @@
 import java.util.List;
 
 @XmlAccessorType(XmlAccessType.FIELD)
 @XmlRootElement(name = "Txn")
 public class Txn {
+    // Purpose code validation - NPCI manifest applied
     @XmlAttribute
     private String custRef;
"""


def main():
    if not REPO_PATH.exists():
        print(f"Repo not found at {REPO_PATH}. Skipping.")
        return
    txn_path = REPO_PATH / "src" / "main" / "java" / "com" / "payer" / "PayerPSP" / "dto" / "Txn.java"
    if not txn_path.exists():
        print(f"Txn.java not found at {txn_path}. Skipping.")
        return
    before = txn_path.read_text(encoding="utf-8")
    if "Purpose code validation" in before:
        print("Marker already in file; reverting for test...")
        before = before.replace("    // Purpose code validation - NPCI manifest applied\n", "")
        txn_path.write_text(before, encoding="utf-8")
    print("Applying sample diff to local repo (no git)...")
    modified = apply_diff_to_dir(SAMPLE_DIFF, REPO_PATH)
    print("Modified files:", modified)
    after = txn_path.read_text(encoding="utf-8")
    if "Purpose code validation" in after:
        print("OK: Patch applied. Txn.java now contains the new comment.")
    else:
        print("FAIL: Txn.java was not updated as expected.")
    # Revert so we don't leave the repo changed
    after = after.replace("    // Purpose code validation - NPCI manifest applied\n", "")
    txn_path.write_text(after, encoding="utf-8")
    print("Reverted Txn.java. Done.")


if __name__ == "__main__":
    main()
