import sys
from unittest.mock import MagicMock
import unittest

# Mock nicegui modules before importing src.ui.bulk_add
sys.modules['nicegui'] = MagicMock()
sys.modules['nicegui.ui'] = MagicMock()
sys.modules['nicegui.run'] = MagicMock()

# We need to ensure src is in path, which it usually is in the sandbox
from src.ui.bulk_add import get_grouping_key_parts

class TestBulkAddGrouping(unittest.TestCase):
    def test_na_format(self):
        # SDK-001 -> NA
        prefix, cat, num = get_grouping_key_parts("SDK-001")
        self.assertEqual(prefix, "SDK")
        self.assertEqual(cat, "NA")
        self.assertEqual(num, "001")

    def test_legacy_eu_format(self):
        # SDK-E001 -> LEGACY_EU
        prefix, cat, num = get_grouping_key_parts("SDK-E001")
        self.assertEqual(prefix, "SDK")
        self.assertEqual(cat, "LEGACY_EU")
        self.assertEqual(num, "001")

    def test_legacy_eu_german_format(self):
        # SDK-G001 -> LEGACY_EU (should match E001)
        prefix, cat, num = get_grouping_key_parts("SDK-G001")
        self.assertEqual(prefix, "SDK")
        self.assertEqual(cat, "LEGACY_EU")
        self.assertEqual(num, "001")

    def test_standard_format_en(self):
        # RA01-EN001 -> STD
        prefix, cat, num = get_grouping_key_parts("RA01-EN001")
        self.assertEqual(prefix, "RA01")
        self.assertEqual(cat, "STD")
        self.assertEqual(num, "001")

    def test_standard_format_de(self):
        # RA01-DE001 -> STD (should match EN001)
        prefix, cat, num = get_grouping_key_parts("RA01-DE001")
        self.assertEqual(prefix, "RA01")
        self.assertEqual(cat, "STD")
        self.assertEqual(num, "001")

    def test_fallback(self):
        # Something weird
        prefix, cat, num = get_grouping_key_parts("XYZ")
        self.assertEqual(prefix, "XYZ")
        self.assertEqual(cat, "UNKNOWN")
        self.assertEqual(num, "000")

if __name__ == '__main__':
    unittest.main()
