import unittest
from src.core.utils import transform_set_code

class TestTransformSetCode(unittest.TestCase):
    def test_no_region_change(self):
        # SDY-006 -> SDY-006 (No region)
        self.assertEqual(transform_set_code('SDY-006', 'DE'), 'SDY-006')
        self.assertEqual(transform_set_code('SDY-006', 'EN'), 'SDY-006')

    def test_standard_region_change(self):
        # LOB-EN001 -> LOB-DE001
        self.assertEqual(transform_set_code('LOB-EN001', 'DE'), 'LOB-DE001')
        self.assertEqual(transform_set_code('LOB-EN001', 'FR'), 'LOB-FR001')

    def test_legacy_region_change(self):
        # LOB-E001 -> LOB-G001 (Legacy E -> G for German)
        self.assertEqual(transform_set_code('LOB-E001', 'DE'), 'LOB-G001')
        self.assertEqual(transform_set_code('LOB-E001', 'FR'), 'LOB-F001')
        self.assertEqual(transform_set_code('LOB-E001', 'IT'), 'LOB-I001')

    def test_mixed_legacy_standard(self):
        # If target language doesn't have legacy code, use standard?
        # REGION_TO_LANGUAGE_MAP has E, G, F, I, S, P.
        # LANGUAGE_TO_LEGACY_REGION_MAP has EN->E, DE->G, FR->F, IT->I, ES->S, PT->P, JP->J, KR->K.

        # Test standard to standard
        self.assertEqual(transform_set_code('RA01-EN001', 'JP'), 'RA01-JP001')

    def test_legacy_to_standard_if_no_legacy_map(self):
        # If I have a legacy code "LOB-E001" and convert to Chinese (ZH).
        # ZH is not in LANGUAGE_TO_LEGACY_REGION_MAP.
        # It should fallback to standard 'ZH'.
        self.assertEqual(transform_set_code('LOB-E001', 'ZH'), 'LOB-ZH001')

    def test_standard_to_legacy(self):
        # If input is standard (LOB-EN001) and target is DE.
        # Code says:
        # match = re.match(r'^([A-Za-z0-9]+)-([A-Za-z]+)(\d+)$', set_code)
        # prefix, region, number
        # new_region_code = lang_code (DE)
        # if len(region) == 1 and region in REGION_TO_LANGUAGE_MAP: ...

        # So if input is 2-letter (EN), it skips the legacy check block.
        # It just returns prefix-DE-number.
        self.assertEqual(transform_set_code('LOB-EN001', 'DE'), 'LOB-DE001')

    def test_legacy_preservation(self):
        # If input is 1-letter (E), and target is DE (G).
        # It enters the block.
        # Returns G.
        self.assertEqual(transform_set_code('LOB-E001', 'DE'), 'LOB-G001')

if __name__ == '__main__':
    unittest.main()
