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
        self.assertTrue(self.view._is_variant_equivalent("LOB-G001", "LOB-DE001", "DE"))

    def test_variant_equivalence_neutral_code(self):
        # GB7-003 (Neutral) vs GB7-DE003 (Standard German)
        # Should return True because neutral codes are allowed to contain any language
        self.assertTrue(self.view._is_variant_equivalent("GB7-003", "GB7-DE003", "DE"))

        # GB7-003 vs GB7-EN003
        self.assertTrue(self.view._is_variant_equivalent("GB7-003", "GB7-EN003", "EN"))

    def test_variant_equivalence_wrong_language(self):
        # LOB-DE001 vs LOB-EN001 (Strictly different languages)
        # Should NOT be equivalent
        self.assertFalse(self.view._is_variant_equivalent("LOB-DE001", "LOB-EN001", "EN"))
        self.assertFalse(self.view._is_variant_equivalent("LOB-EN001", "LOB-DE001", "DE"))

if __name__ == '__main__':
    unittest.main()
