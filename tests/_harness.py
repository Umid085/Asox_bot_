"""Tashqi bog'liqliksiz mayda test yordamchisi (pytest talab qilinmaydi)."""
import logging
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
for path in (str(REPO_ROOT), str(REPO_ROOT / "tests")):
    if path not in sys.path:
        sys.path.insert(0, path)

logging.disable(logging.CRITICAL)


class Results:
    def __init__(self):
        self.passed = 0
        self.failed = 0

    def check(self, label, condition):
        if condition:
            self.passed += 1
            print(f"  ✅ {label}")
        else:
            self.failed += 1
            print(f"  ❌ {label}")
        return bool(condition)

    def summary(self, title):
        print(f"\n{'=' * 46}")
        print(f"  {title}: ✅ {self.passed} ta o'tdi   ❌ {self.failed} ta yiqildi")
        print("=" * 46)
        return 1 if self.failed else 0
