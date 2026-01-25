import unittest
from src.ui.components.single_card_view import SingleCardView

class TestSingleCardViewLogic(unittest.TestCase):
    def setUp(self):
        self.view = SingleCardView()

    def test_variant_equivalence_exact_match(self):
        # Exact match should always return True
        self.assertTrue(self.view._is_variant_equivalent("LOB-EN001", "LOB-EN001", "EN"))
        self.assertTrue(self.view._is_variant_equivalent("LOB-DE001", "LOB-DE001", "DE"))

    def test_variant_equivalence_legacy_german(self):
        # LOB-G001 (Legacy German) vs LOB-DE001 (Standard German)
        # Should be equivalent if language is DE
        self.assertTrue(self.view._is_variant_equivalent("LOB-G001", "LOB-DE001", "DE"))

    def test_variant_equivalence_wrong_language(self):
        # LOB-G001 (German) vs LOB-EN001 (English)
        # Should NOT be equivalent
        self.assertFalse(self.view._is_variant_equivalent("LOB-G001", "LOB-EN001", "EN"))

        # Even if we ask if it's equivalent for "DE", if target is EN code...
        # But wait, target_set_code is usually computed for the target language.
        # If target_set_code is LOB-EN001, normalize is LOB-001.
        # LOB-G001 normalize is LOB-001.
        # If target_language is "DE".
        # extract_language_code("LOB-G001") is "DE".
        # So it returns True?

        # If I select "DE", but the base code transforms to "LOB-EN001" (because transform failed to change region?)
        # Ideally transform should give LOB-DE001.

        # Test: target is "LOB-DE001", language "DE". Variant "LOB-EN001".
        # normalize matches. extract("LOB-EN001") -> "EN".
        # EN != DE. Returns False. Correct.
        self.assertFalse(self.view._is_variant_equivalent("LOB-EN001", "LOB-DE001", "DE"))

    def test_variant_equivalence_no_region_code(self):
        # LOB-001 (No region, usually NA/EN)
        # If target is LOB-001.
        self.assertTrue(self.view._is_variant_equivalent("LOB-001", "LOB-001", "EN"))

        # If I have LOB-001 and I select DE.
        # target code: LOB-001 (transform doesn't add region if missing)
        # variant: LOB-001.
        # Exact match -> True.
        self.assertTrue(self.view._is_variant_equivalent("LOB-001", "LOB-001", "DE"))

        # But wait, logic:
        # if LOB-001 == LOB-001 -> True.
        # Correct.

    def test_variant_equivalence_legacy_asian_english(self):
        # Not explicitly supported map but let's check behavior if it existed
        pass

if __name__ == '__main__':
    unittest.main()
