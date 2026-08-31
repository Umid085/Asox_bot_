"""Barcha test to'plamlarini ishga tushiradi:  python3 tests/run_all.py"""
import asyncio
import sys

from _harness import Results  # sys.path ni sozlaydi

import test_firestore_layer
import test_middleware
import test_normalization
import test_rendering

SUITES = [
    ("Normalizatsiya va xavfsizlik", test_normalization),
    ("Firestore qatlami", test_firestore_layer),
    ("Render, kirish tekshiruvi, xatoliklar", test_rendering),
    ("Throttling va telefon", test_middleware),
]

def main() -> int:
    failures = 0
    for title, module in SUITES:
        print(f"\n{'#' * 46}\n#  {title}\n{'#' * 46}")
        failures += asyncio.run(module.main())
    print("\n🎉 Barcha to'plamlar o'tdi." if not failures else f"\n💥 {failures} ta to'plam yiqildi.")
    return failures

if __name__ == "__main__":
    sys.exit(main())
