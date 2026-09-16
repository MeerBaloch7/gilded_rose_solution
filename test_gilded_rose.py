import pytest
from gilded_rose import Item, GildedRose


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def update(items, days=1):
    """Run update_quality() for `days` days and return the item list."""
    app = GildedRose(items)
    for _ in range(days):
        app.update_quality()
    return items


def make(name, sell_in, quality):
    """Convenience factory so tests stay concise."""
    return Item(name, sell_in, quality)


# ---------------------------------------------------------------------------
# 1. NORMAL ITEMS
# ---------------------------------------------------------------------------

class TestNormalItems:
    """Standard items with no special rules."""

    def test_quality_decreases_by_1_before_sell_date(self):
        item = make("+5 Dexterity Vest", sell_in=10, quality=20)
        update([item])
        assert item.quality == 19

    def test_sell_in_decreases_by_1_each_day(self):
        item = make("+5 Dexterity Vest", sell_in=10, quality=20)
        update([item])
        assert item.sell_in == 9

    def test_quality_decreases_by_2_after_sell_date_passes(self):
        item = make("Elixir of the Mongoose", sell_in=0, quality=10)
        update([item])
        assert item.quality == 8

    def test_quality_degrades_twice_as_fast_once_sell_by_passed(self):
        # sell_in goes negative: each day costs 2 quality
        item = make("Elixir of the Mongoose", sell_in=1, quality=10)
        update([item], days=2)          
        assert item.quality == 7

    def test_quality_never_goes_negative(self):
        item = make("+5 Dexterity Vest", sell_in=5, quality=0)
        update([item])
        assert item.quality == 0

    def test_quality_never_goes_negative_after_expiry(self):
        item = make("+5 Dexterity Vest", sell_in=0, quality=1)
        update([item])                  
        assert item.quality == 0

    def test_quality_drops_to_zero_not_below_over_many_days(self):
        item = make("+5 Dexterity Vest", sell_in=2, quality=3)
        update([item], days=10)
        assert item.quality == 0

    def test_sell_in_continues_to_decrease_after_expiry(self):
        item = make("+5 Dexterity Vest", sell_in=0, quality=10)
        update([item], days=3)
        assert item.sell_in == -3


# ---------------------------------------------------------------------------
# 2. AGED BRIE
# ---------------------------------------------------------------------------

class TestAgedBrie:
    """Aged Brie increases in quality the older it gets."""

    def test_quality_increases_by_1_before_sell_date(self):
        item = make("Aged Brie", sell_in=5, quality=10)
        update([item])
        assert item.quality == 11

    def test_sell_in_decreases_normally(self):
        item = make("Aged Brie", sell_in=5, quality=10)
        update([item])
        assert item.sell_in == 4

    def test_quality_increases_by_2_after_sell_date(self):
        item = make("Aged Brie", sell_in=0, quality=10)
        update([item])
        assert item.quality == 12

    def test_quality_never_exceeds_50(self):
        item = make("Aged Brie", sell_in=5, quality=50)
        update([item])
        assert item.quality == 50

    def test_quality_caps_at_50_even_after_sell_date(self):
        item = make("Aged Brie", sell_in=0, quality=49)
        update([item])                  # would want +2 but cap is 50
        assert item.quality == 50

    def test_quality_caps_at_50_over_many_days(self):
        item = make("Aged Brie", sell_in=20, quality=0)
        update([item], days=60)
        assert item.quality == 50

    def test_quality_at_exactly_50_stays_at_50(self):
        item = make("Aged Brie", sell_in=2, quality=50)
        update([item], days=5)
        assert item.quality == 50


# ---------------------------------------------------------------------------
# 3. SULFURAS
# ---------------------------------------------------------------------------

class TestSulfuras:
    """Sulfuras is a legendary item — it never changes."""

    SULFURAS = "Sulfuras, Hand of Ragnaros"

    def test_quality_never_changes(self):
        item = make(self.SULFURAS, sell_in=0, quality=80)
        update([item])
        assert item.quality == 80

    def test_sell_in_never_changes(self):
        item = make(self.SULFURAS, sell_in=0, quality=80)
        update([item])
        assert item.sell_in == 0

    def test_quality_stays_at_80_over_many_days(self):
        item = make(self.SULFURAS, sell_in=0, quality=80)
        update([item], days=30)
        assert item.quality == 80

    def test_sell_in_stays_negative_if_negative(self):
        item = make(self.SULFURAS, sell_in=-1, quality=80)
        update([item], days=5)
        assert item.sell_in == -1

    def test_quality_is_80_and_never_alters(self):
        """Legendary quality is always 80 — not subject to normal cap rules."""
        item = make(self.SULFURAS, sell_in=5, quality=80)
        update([item], days=10)
        assert item.quality == 80
        assert item.sell_in == 5


# ---------------------------------------------------------------------------
# 4. BACKSTAGE PASSES
# ---------------------------------------------------------------------------

class TestBackstagePasses:
    """
    Quality increases as sell_in approaches:
      > 10 days  → +1/day
      ≤ 10 days  → +2/day
      ≤  5 days  → +3/day
    After concert (sell_in < 0) → quality drops to 0.
    """

    PASS = "Backstage passes to a TAFKAL80ETC concert"

    def test_quality_increases_by_1_when_more_than_10_days(self):
        item = make(self.PASS, sell_in=15, quality=20)
        update([item])
        assert item.quality == 21

    def test_sell_in_decreases_normally(self):
        item = make(self.PASS, sell_in=15, quality=20)
        update([item])
        assert item.sell_in == 14

    def test_quality_increases_by_2_when_10_days_or_less(self):
        item = make(self.PASS, sell_in=10, quality=20)
        update([item])
        assert item.quality == 22

    def test_quality_increases_by_2_when_exactly_10_days(self):
        item = make(self.PASS, sell_in=10, quality=30)
        update([item])
        assert item.quality == 32

    def test_quality_increases_by_2_at_6_days(self):
        item = make(self.PASS, sell_in=6, quality=30)
        update([item])
        assert item.quality == 32

    def test_quality_increases_by_3_when_5_days_or_less(self):
        item = make(self.PASS, sell_in=5, quality=20)
        update([item])
        assert item.quality == 23

    def test_quality_increases_by_3_at_exactly_5_days(self):
        item = make(self.PASS, sell_in=5, quality=40)
        update([item])
        assert item.quality == 43

    def test_quality_increases_by_3_at_1_day(self):
        item = make(self.PASS, sell_in=1, quality=30)
        update([item])
        assert item.quality == 33

    def test_quality_drops_to_0_after_concert(self):
        item = make(self.PASS, sell_in=0, quality=50)
        update([item])
        assert item.quality == 0

    def test_quality_is_0_after_concert_regardless_of_original_quality(self):
        item = make(self.PASS, sell_in=0, quality=20)
        update([item])
        assert item.quality == 0

    def test_quality_stays_0_many_days_after_concert(self):
        item = make(self.PASS, sell_in=0, quality=40)
        update([item], days=5)
        assert item.quality == 0

    def test_quality_never_exceeds_50(self):
        item = make(self.PASS, sell_in=5, quality=50)
        update([item])
        assert item.quality == 50

    def test_quality_caps_at_50_in_10_day_window(self):
        item = make(self.PASS, sell_in=10, quality=49)
        update([item])                  # wants +2 but cap is 50
        assert item.quality == 50

    def test_quality_caps_at_50_in_5_day_window(self):
        item = make(self.PASS, sell_in=5, quality=49)
        update([item])                  # wants +3 but cap is 50
        assert item.quality == 50

    def test_full_lifecycle(self):
        """Walk a pass from 12 days out through the concert."""
        item = make(self.PASS, sell_in=12, quality=20)
        update([item], days=2)          # 12→10: +1 each day  → q=22
        assert item.quality == 22
        update([item], days=5)          # 10→5:  +2 each day  → q=32
        assert item.quality == 32
        update([item], days=5)          # 5→0:   +3 each day  → q=47
        assert item.quality == 47
        update([item])                  # concert day passes  → q=0
        assert item.quality == 0


# ---------------------------------------------------------------------------
# 5. CONJURED ITEMS
# ---------------------------------------------------------------------------

class TestConjuredItems:
    """
    Conjured items degrade in quality twice as fast as normal items.
    Assumption: any item whose name starts with 'Conjured' is treated
    as a Conjured item.
    """

    def test_quality_decreases_by_2_before_sell_date(self):
        item = make("Conjured Mana Cake", sell_in=5, quality=10)
        update([item])
        assert item.quality == 8

    def test_sell_in_decreases_normally(self):
        item = make("Conjured Mana Cake", sell_in=5, quality=10)
        update([item])
        assert item.sell_in == 4

    def test_quality_decreases_by_4_after_sell_date(self):
        item = make("Conjured Mana Cake", sell_in=0, quality=10)
        update([item])
        assert item.quality == 6

    def test_quality_never_goes_negative(self):
        item = make("Conjured Mana Cake", sell_in=5, quality=1)
        update([item])
        assert item.quality == 0

    def test_quality_never_goes_negative_after_expiry(self):
        item = make("Conjured Mana Cake", sell_in=0, quality=3)
        update([item])                  # wants -4 but floor is 0
        assert item.quality == 0

    def test_quality_at_zero_stays_zero(self):
        item = make("Conjured Mana Cake", sell_in=5, quality=0)
        update([item])
        assert item.quality == 0

    def test_quality_drops_to_zero_not_below_over_many_days(self):
        item = make("Conjured Mana Cake", sell_in=3, quality=6)
        update([item], days=10)
        assert item.quality == 0

    def test_degrades_twice_as_fast_as_normal_item(self):
        """Direct comparison: conjured vs normal with same starting values."""
        normal  = make("Elixir of the Mongoose", sell_in=5, quality=20)
        conjured = make("Conjured Mana Cake",     sell_in=5, quality=20)
        update([normal, conjured])
        assert conjured.quality == normal.quality - 1   # conjured -2, normal -1


# ---------------------------------------------------------------------------
# 6. EDGE CASES
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """Boundary and cross-cutting constraints."""

    def test_quality_floor_is_0_for_all_normal_items(self):
        items = [
            make("+5 Dexterity Vest", sell_in=0, quality=0),
            make("Elixir of the Mongoose", sell_in=0, quality=0),
        ]
        update(items)
        for item in items:
            assert item.quality == 0

    def test_quality_ceiling_is_50_for_non_legendary_items(self):
        items = [
            make("Aged Brie", sell_in=5, quality=50),
            make("Backstage passes to a TAFKAL80ETC concert", sell_in=5, quality=50),
        ]
        update(items)
        for item in items:
            assert item.quality == 50

    def test_sulfuras_quality_exceeds_normal_cap_legitimately(self):
        item = make("Sulfuras, Hand of Ragnaros", sell_in=0, quality=80)
        update([item])
        assert item.quality == 80      # 80 > 50 is valid only for Sulfuras

    def test_multiple_items_update_independently(self):
        items = [
            make("+5 Dexterity Vest", sell_in=5, quality=20),
            make("Aged Brie", sell_in=5, quality=10),
            make("Sulfuras, Hand of Ragnaros", sell_in=0, quality=80),
        ]
        update(items)
        assert items[0].quality == 19   # normal: -1
        assert items[1].quality == 11   # brie: +1
        assert items[2].quality == 80   # sulfuras: unchanged

    def test_sell_in_can_go_deeply_negative(self):
        item = make("+5 Dexterity Vest", sell_in=0, quality=50)
        update([item], days=10)
        assert item.sell_in == -10

    def test_quality_never_negative_with_large_time_jump(self):
        items = [
            make("+5 Dexterity Vest", sell_in=2, quality=5),
            make("Conjured Mana Cake", sell_in=2, quality=5),
        ]
        update(items, days=20)
        for item in items:
            assert item.quality >= 0

    def test_item_with_zero_quality_at_zero_sell_in(self):
        """Verify floor holds even under the double-degradation rule."""
        item = make("+5 Dexterity Vest", sell_in=0, quality=0)
        update([item])
        assert item.quality == 0

    def test_backstage_pass_at_sell_in_11_gets_plus_1(self):
        """Boundary: 11 days is NOT in the ≤10 window."""
        item = make("Backstage passes to a TAFKAL80ETC concert", sell_in=11, quality=20)
        update([item])
        assert item.quality == 21

    def test_backstage_pass_at_sell_in_10_gets_plus_2(self):
        """Boundary: exactly 10 days triggers the +2 window."""
        item = make("Backstage passes to a TAFKAL80ETC concert", sell_in=10, quality=20)
        update([item])
        assert item.quality == 22

    def test_backstage_pass_at_sell_in_6_gets_plus_2(self):
        """Boundary: 6 days is NOT in the ≤5 window."""
        item = make("Backstage passes to a TAFKAL80ETC concert", sell_in=6, quality=20)
        update([item])
        assert item.quality == 22

    def test_backstage_pass_at_sell_in_5_gets_plus_3(self):
        """Boundary: exactly 5 days triggers the +3 window."""
        item = make("Backstage passes to a TAFKAL80ETC concert", sell_in=5, quality=20)
        update([item])
        assert item.quality == 23


if __name__ == "__main__":
    pytest.main([__file__, "-v"])