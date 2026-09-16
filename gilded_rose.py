# -*- coding: utf-8 -*-
from updaters import (
    NormalItemUpdater,
    AgedBrieUpdater,
    SulfurasUpdater,
    BackstagePassUpdater,
    ConjuredItemUpdater,
)


class GildedRose(object):
    """
    Inventory manager for the Gilded Rose inn.

    update_quality() is called once per day and delegates to a
    per-item-type updater. Adding a new item category requires only:
      1. A new updater class in updaters.py
      2. One new entry in UPDATERS below
    Nothing else changes.

    Assumption: any item whose name starts with 'Conjured' (case-insensitive)
    is treated as a Conjured item. The spec introduces Conjured as a category
    of items, not a single fixed product name.
    """

    # Map exact item names → their updater instance.
    # Looked up first; the Conjured prefix check is the fallback.
    UPDATERS = {
        "Aged Brie":                                    AgedBrieUpdater(),
        "Sulfuras, Hand of Ragnaros":                   SulfurasUpdater(),
        "Backstage passes to a TAFKAL80ETC concert":    BackstagePassUpdater(),
    }

    def _get_updater(self, item):
        """
        Return the correct updater for this item.

        Resolution order:
          1. Exact name match in UPDATERS dict  (O(1) lookup)
          2. Name starts with 'Conjured'        (category rule)
          3. Default → NormalItemUpdater
        """
        if item.name in self.UPDATERS:
            return self.UPDATERS[item.name]
        if item.name.lower().startswith("conjured"):
            return ConjuredItemUpdater()
        return NormalItemUpdater()

    def update_quality(self):
        for item in self.items:
            self._get_updater(item).update(item)

    def __init__(self, items):
        self.items = items


# ---------------------------------------------------------------------------
# Item — DO NOT MODIFY
# The goblin in the corner will insta-rage. Shared code ownership is not
# something he believes in.
# ---------------------------------------------------------------------------

class Item:
    def __init__(self, name, sell_in, quality):
        self.name = name
        self.sell_in = sell_in
        self.quality = quality

    def __repr__(self):
        return "%s, %s, %s" % (self.name, self.sell_in, self.quality)