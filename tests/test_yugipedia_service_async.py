
import unittest
import asyncio
from unittest.mock import MagicMock, patch
from src.services.yugipedia_service import YugipediaService

class TestYugipediaServiceAsync(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.service = YugipediaService()

    @patch('src.services.yugipedia_service.run.io_bound')
    async def test_get_all_decks(self, mock_get):
        # Mock Response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "query": {
                "results": {
                    "Structure Deck: Test": {
                        "printouts": {
                            "English set prefix": ["SD01"]
                        }
                    },
                    "Speed Duel Starter Decks: Test Speed": {
                         "printouts": {
                            "English set prefix": ["SS01"]
                        }
                    },
                    "Starter Deck: Standard": {
                         "printouts": {
                            "English set prefix": ["ST01"]
                        }
                    }
                }
            }
        }
        mock_get.return_value = mock_response

        decks = await self.service.get_all_decks()

        # Verify
        self.assertEqual(len(decks), 3)

        # Find decks
        sd = next(d for d in decks if d.title == "Structure Deck: Test")
        speed = next(d for d in decks if d.title == "Speed Duel Starter Decks: Test Speed")
        starter = next(d for d in decks if d.title == "Starter Deck: Standard")

        self.assertEqual(sd.code, "SD01")
        # Overlap handling test:
        # Since mock returns it for both Structure and Starter calls, and Structure is processed first,
        # it gets 'STRUCTURE'. Then Starter processing sees it exists and ignores it (unless it was Speed).
        self.assertEqual(sd.deck_type, "STRUCTURE")

        self.assertEqual(speed.code, "SS01")
        self.assertEqual(speed.deck_type, "SPEED")

        self.assertEqual(starter.code, "ST01")
        # Overlap handling: "Starter Deck: Standard" returned for Structure call -> STRUCTURE.
        # This is expected behavior for the MOCK, not necessarily real life.
        self.assertEqual(starter.deck_type, "STRUCTURE")

    @patch('src.services.yugipedia_service.run.io_bound')
    async def test_get_all_decks_pagination(self, mock_get):
         def side_effect(*args, **kwargs):
             params = kwargs.get('params', {})
             query = params.get('query', '')
             offset = 0
             import re
             m = re.search(r'offset=(\d+)', query)
             if m: offset = int(m.group(1))

             resp = MagicMock()
             resp.status_code = 200

             if "Structure" in query:
                 if offset == 0:
                     resp.json.return_value = {
                        "query": {"results": {"Struct 1": {"printouts": {"English set prefix": ["S1"]}}}},
                        "query-continue-offset": 500
                     }
                 else:
                     resp.json.return_value = {
                        "query": {"results": {"Struct 2": {"printouts": {"English set prefix": ["S2"]}}}}
                     }
             else: # Starter
                 resp.json.return_value = {
                    "query": {"results": {"Start 1": {"printouts": {"English set prefix": ["ST1"]}}}}
                 }
             return resp

         mock_get.side_effect = side_effect

         decks = await self.service.get_all_decks()

         self.assertEqual(len(decks), 3)
         titles = sorted([d.title for d in decks])
         self.assertEqual(titles, ["Start 1", "Struct 1", "Struct 2"])

if __name__ == '__main__':
    unittest.main()
