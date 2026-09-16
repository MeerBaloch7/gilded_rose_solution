# -*- coding: utf-8 -*-
from updaters import (
    NormalItemUpdater,
    AgedBrieUpdater,
    SulfurasUpdater,
    BackstagePassUpdater,
    ConjuredItemUpdater,
)


class GildedRose(object):

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
# ---------------------------------------------------------------------------

class Item:
    def __init__(self, name, sell_in, quality):
        self.name = name
        self.sell_in = sell_in
        self.quality = quality

    def __repr__(self):
        return "%s, %s, %s" % (self.name, self.sell_in, self.quality)