# Gilded Rose — Refactoring Kata (Python)

**Submission by:** Meer Muhammad  
**Role:** AI Product Developer  
**Language:** Python 3  
**Challenge:** [TechieMinions Gilded Rose Refactoring Kata](https://github.com/TechieMinions/GildedRose-Refactoring-Kata)

---

## Project Structure

```
gilded_rose_solution/
├── gilded_rose.py          # GildedRose dispatcher + untouched Item class
├── updaters.py             # One updater class per item type (strategy pattern)
├── test_gilded_rose.py     # 54 unit tests written against the spec (pytest)
├── texttest_fixture.py     # Original acceptance fixture (unchanged)
└── README.md               # This file
```

---

## How to Run

**Install dependencies**
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install pytest
```

**Run the test suite**
```bash
pytest test_gilded_rose.py -v
```

Expected output: **54 passed**

**Run the acceptance fixture**
```bash
python texttest_fixture.py 10
```

---

## What the Original Code Was Doing Wrong

The original `update_quality()` method was a single function with **6 levels of nested conditionals** spanning 30 lines. The core problems:

| Bug | Detail |
|-----|--------|
| **Conjured items unimplemented** | Conjured items were treated as normal items, degrading by 1/day instead of 2 |
| **No separation of concerns** | All item logic was tangled in one block — impossible to read, test, or extend independently |
| **Fragile quality cap checks** | The 50-cap was checked inline mid-calculation rather than enforced as a single constraint |
| **Broken starter test** | The provided `test_foo` asserted `"fixme"` as the item name — designed to always fail |

---

## Approach

### Step 1 — Understand the spec, read the code

Mapped every business rule from the README to the original code and identified exactly what was missing and what was working by accident.

### Step 2 — Write tests against the spec, not the buggy code

54 tests across 6 classes, written **before** touching the implementation. Running them against the original code produced exactly **4 failures — all on Conjured items** — which precisely pinpointed the bug.

### Step 3 — Create `updaters.py` (strategy pattern)

One class per item type. Each class owns exactly one responsibility: how that item's quality and sell_in change per day.

```
ItemUpdater          ← abstract base (template method)
├── SulfurasUpdater       → no-op (frozen forever)
├── NormalItemUpdater     → -1/day, -2 after expiry
├── AgedBrieUpdater       → +1/day, +2 after expiry
├── BackstagePassUpdater  → tiered +1/+2/+3, drops to 0 after concert
└── ConjuredItemUpdater   → -2/day, -4 after expiry  ← new feature
```

A shared `_clamp(quality)` helper enforces `0 ≤ quality ≤ 50` in one place across all updaters.

### Step 4 — Refactor `gilded_rose.py` to a thin dispatcher

`update_quality()` went from 30 lines of nested conditionals to 3 lines:

```python
def update_quality(self):
    for item in self.items:
        self._get_updater(item).update(item)
```

`_get_updater()` resolves the right updater via: exact name dict lookup → Conjured prefix check → NormalItemUpdater default.

---

## Design Decisions

**Why the strategy pattern?**  
Each item type has fundamentally different behaviour. Encoding all of that in one function with string comparisons is an `if/elif` chain waiting to grow forever. Classes give each item type a home with its own logic, its own docstring, and its own tests. Adding a new item type in future = one new class and one new dict entry. Nothing else changes. This is the Open/Closed Principle applied directly.

**Why `_clamp()` as a module-level function?**  
It is a pure function over an integer — it needs no `self`. Keeping it at module level means every updater class can call it with no ceremony, and it can be tested in complete isolation.

**Why does `_update_quality` run before `sell_in` decrements?**  
The quality check for expiry uses `sell_in <= 0`, which means "today is already past the sell date." If the decrement ran first, the boundary would be off by one and Backstage Pass thresholds would fire a day early.

**Why is the `Item` class completely untouched?**  
The brief is explicit: the goblin in the corner will insta-rage. The `Item` class is byte-for-byte identical to the original. All changes are isolated to `GildedRose` and the new `updaters.py`.

---

## Assumption (stated clearly)

The spec says *"Conjured items degrade in quality twice as fast as normal items"* — referring to a **category**, not a single product. The fixture uses `"Conjured Mana Cake"` as an example. 

**Assumption:** any item whose name starts with `"Conjured"` (case-insensitive) is treated as a Conjured item.

This is documented in both `gilded_rose.py` and `updaters.py`.

---

## Test Coverage Summary

| Class | Tests | What is covered |
|-------|-------|-----------------|
| `TestNormalItems` | 8 | Before/after expiry, floor at 0, sell_in tracking |
| `TestAgedBrie` | 7 | Increment, double after expiry, cap at 50 |
| `TestSulfuras` | 5 | Quality and sell_in completely frozen |
| `TestBackstagePasses` | 15 | All three thresholds, boundary values (10, 5), drops to 0, cap, full lifecycle |
| `TestConjuredItems` | 8 | -2/-4 degradation, floor, comparison vs normal |
| `TestEdgeCases` | 11 | Floors, ceilings, multi-item independence, deep sell_in negativity |
| **Total** | **54** | **54 passed** |

---
