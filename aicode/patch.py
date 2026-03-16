import difflib
from patch_generator import generate_java_patch

REQPAY_FILE = r"C:\Users\kalai\OneDrive\Desktop\Phase2 Sample code\UPISim\src\main\java\com\npci\UPISim\service\ReqPayService.java"


def generate_patch(payload):
    with open(REQPAY_FILE, "r", encoding="utf-8") as f:
        original = f.read()

    updated = generate_java_patch(original, payload)

    diff = "\n".join(
        difflib.unified_diff(
            original.splitlines(),
            updated.splitlines(),
            fromfile="OLD",
            tofile="NEW"
        )
    )

    return {
        "file": REQPAY_FILE,
        "old": original,
        "new": updated,
        "diff": diff
    }
