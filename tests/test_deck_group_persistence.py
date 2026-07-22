import os
import shutil
import unittest

from src.core.models import Deck
from src.core.persistence import PersistenceManager


class TestDeckGroupPersistence(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_data_deck_groups"
        self.decks_dir = os.path.join(self.test_dir, "decks")
        self.pm = PersistenceManager(
            data_dir=os.path.join(self.test_dir, "collections"),
            decks_dir=self.decks_dir,
        )

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_grouped_decks_are_isolated(self):
        self.pm.save_deck(Deck(name="Root", main=[1]), "Shared.ydk")
        self.pm.save_deck(Deck(name="Group", main=[2]), "Shared.ydk", "Favorites")

        self.assertEqual(self.pm.list_deck_groups(), ["Favorites", "main"])
        self.assertEqual(self.pm.load_deck("Shared.ydk").main, [1])
        self.assertEqual(self.pm.load_deck("Shared.ydk", "Favorites").main, [2])

    def test_rejects_deck_filename_path_traversal(self):
        deck = Deck(name="Traversal", main=[123])

        with self.assertRaises(ValueError):
            self.pm.save_deck(deck, "../escaped.ydk")

        with self.assertRaises(ValueError):
            self.pm.save_deck_content("#main\n123\n", "../escaped.ydk", "Favorites")

        self.assertFalse(os.path.exists(os.path.join(self.test_dir, "escaped.ydk")))

    def test_move_deck_transfers_it_between_groups(self):
        self.pm.save_deck(Deck(name="To Move", main=[42]), "To Move.ydk", "Source")

        self.pm.move_deck("To Move.ydk", "Source", "Destination")

        self.assertEqual(self.pm.list_decks("Source"), [])
        self.assertEqual(self.pm.load_deck("To Move.ydk", "Destination").main, [42])

    def test_move_deck_does_not_overwrite_destination(self):
        self.pm.save_deck(Deck(name="Source", main=[1]), "Shared.ydk", "Source")
        self.pm.save_deck(Deck(name="Destination", main=[2]), "Shared.ydk", "Destination")

        with self.assertRaises(FileExistsError):
            self.pm.move_deck("Shared.ydk", "Source", "Destination")

        self.assertEqual(self.pm.load_deck("Shared.ydk", "Source").main, [1])
        self.assertEqual(self.pm.load_deck("Shared.ydk", "Destination").main, [2])

    def test_move_deck_rejects_case_insensitive_destination_collision(self):
        self.pm.save_deck(Deck(name="Source", main=[1]), "MyDeck.ydk", "Source")
        self.pm.save_deck(Deck(name="Destination", main=[2]), "mydeck.ydk", "Destination")

        with self.assertRaises(FileExistsError):
            self.pm.move_deck("MyDeck.ydk", "Source", "Destination")

        self.assertEqual(self.pm.load_deck("MyDeck.ydk", "Source").main, [1])
        self.assertEqual(self.pm.load_deck("mydeck.ydk", "Destination").main, [2])


if __name__ == "__main__":
    unittest.main()
