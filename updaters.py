# -*- coding: utf-8 -*-
"""
updaters.py — Item update strategy classes for the Gilded Rose.

One class per item type. Each class owns exactly one responsibility:
deciding how a single item's quality and sell_in change at end of day.

Rules that apply to every updater:
  - Quality is never negative
  - Quality never exceeds 50  (except Sulfuras, which is fixed at 80)
  - sell_in decrements every day (except Sulfuras, which never changes)

Adding a new item category in future = add one new class here.
Nothing else changes. (Open/Closed Principle)
"""

MIN_QUALITY = 0
MAX_QUALITY = 50


# ---------------------------------------------------------------------------
# Shared helper
# ---------------------------------------------------------------------------

def _clamp(quality: int) -> int:
    """
    Enforce the quality floor (0) and ceiling (50).
    All updaters call this instead of doing bounds checks inline.
    Sulfuras bypasses this entirely — its quality is legendary (80).
    """
    return max(MIN_QUALITY, min(MAX_QUALITY, quality))


# ---------------------------------------------------------------------------
# Base class
# ---------------------------------------------------------------------------

class ItemUpdater:
    """
    Abstract base for all item updaters.

    Subclasses must implement `_update_quality(item)`, which contains
    the item-specific quality logic. The base `update()` method handles
    the shared sell_in decrement that applies to every non-legendary item.
    """

    def update(self, item) -> None:
        """
        Template method: run quality logic first, then decrement sell_in.
        Subclasses override `_update_quality`, not this method.
        """
        self._update_quality(item)
        self._decrement_sell_in(item)

    def _update_quality(self, item) -> None:
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement _update_quality()"
        )

    def _decrement_sell_in(self, item) -> None:
        item.sell_in -= 1

    @property
    def _expired(self):
        """
        Convenience used by subclasses: check if sell_in has already
        hit 0 before today's decrement (i.e. today is the last sell day,
        tomorrow it will be negative). Checked AFTER quality update
        but BEFORE decrement — so the threshold is sell_in <= 0.
        """
        # Not used as a property here — subclasses receive `item` and
        # do their own `item.sell_in <= 0` check. Kept as a docstring
        # reminder of the convention.
        pass


# ---------------------------------------------------------------------------
# 1. Sulfuras  (simplest — do absolutely nothing)
# ---------------------------------------------------------------------------

class SulfurasUpdater(ItemUpdater):
    """
    Sulfuras, Hand of Ragnaros — a legendary item.

    It never has to be sold and never decreases in quality.
    Quality is fixed at 80 (above the normal cap of 50).
    Both quality and sell_in are completely frozen.
    """

    def update(self, item) -> None:
        # Override the full template: Sulfuras skips sell_in decrement too.
        pass  # Nothing. Ever. Legendary.

    def _update_quality(self, item) -> None:
        pass  # Satisfies the interface; never called because update() is overridden.


# ---------------------------------------------------------------------------
# 2. Normal items
# ---------------------------------------------------------------------------

class NormalItemUpdater(ItemUpdater):
    """
    Standard inventory items (e.g. '+5 Dexterity Vest', 'Elixir of the Mongoose').

    Quality degrades by 1 each day before the sell-by date.
    Quality degrades by 2 each day once the sell-by date has passed.
    Quality never falls below 0.
    """

    def _update_quality(self, item) -> None:
        degradation = 2 if item.sell_in <= 0 else 1
        item.quality = _clamp(item.quality - degradation)


# ---------------------------------------------------------------------------
# 3. Aged Brie
# ---------------------------------------------------------------------------

class AgedBrieUpdater(ItemUpdater):
    """
    Aged Brie — increases in quality the older it gets.

    Quality increases by 1 each day before the sell-by date.
    Quality increases by 2 each day once the sell-by date has passed.
    Quality never exceeds 50.
    """

    def _update_quality(self, item) -> None:
        appreciation = 2 if item.sell_in <= 0 else 1
        item.quality = _clamp(item.quality + appreciation)


# ---------------------------------------------------------------------------
# 4. Backstage passes
# ---------------------------------------------------------------------------

class BackstagePassUpdater(ItemUpdater):
    """
    Backstage passes to a TAFKAL80ETC concert.

    Quality increases as the concert approaches, then crashes to 0 after.

    Schedule:
      sell_in > 10 days  →  +1 quality per day
      sell_in 6–10 days  →  +2 quality per day
      sell_in 1–5 days   →  +3 quality per day
      sell_in <= 0       →  quality drops to 0 (concert has passed)

    Quality never exceeds 50 while the concert is upcoming.
    """

    def _update_quality(self, item) -> None:
        if item.sell_in <= 0:
            # Concert has passed — the pass is worthless.
            item.quality = 0
        elif item.sell_in <= 5:
            item.quality = _clamp(item.quality + 3)
        elif item.sell_in <= 10:
            item.quality = _clamp(item.quality + 2)
        else:
            item.quality = _clamp(item.quality + 1)


# ---------------------------------------------------------------------------
# 5. Conjured items
# ---------------------------------------------------------------------------

class ConjuredItemUpdater(ItemUpdater):
    """
    Conjured items — degrade in quality twice as fast as normal items.

    Assumption: any item whose name starts with 'Conjured' (case-insensitive)
    belongs to this category. The spec introduces it as a category ('conjured
    items'), not a single named product. Stated assumption is documented here
    and in gilded_rose.py for the reviewer.

    Quality degrades by 2 each day before the sell-by date.
    Quality degrades by 4 each day once the sell-by date has passed.
    Quality never falls below 0.
    """

    def _update_quality(self, item) -> None:
        degradation = 4 if item.sell_in <= 0 else 2
        item.quality = _clamp(item.quality - degradation)