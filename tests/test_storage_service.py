import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Mock dependencies that are missing in the environment
mock_nicegui = MagicMock()
sys.modules['nicegui'] = mock_nicegui
sys.modules['nicegui.run'] = MagicMock()

mock_pydantic = MagicMock()
class MockBaseModel:
    def __init__(self, **data):
        for k, v in data.items():
            setattr(self, k, v)
    def model_dump(self):
        # Basic implementation to satisfy StorageService.get_storage and get_all_storage
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

mock_pydantic.BaseModel = MockBaseModel
mock_pydantic.Field = MagicMock(return_value=None)
sys.modules['pydantic'] = mock_pydantic

# Now import the service and models
from src.services.storage import StorageService
from src.core.models import Collection, StorageDefinition

class TestStorageService(unittest.TestCase):
    @patch('os.makedirs')
    def setUp(self, mock_makedirs):
        self.service = StorageService()
        # Initialize collection with required fields
        self.collection = Collection(name="Test Collection", storage_definitions=[])

    def test_get_all_storage(self):
        # Empty collection
        self.assertEqual(self.service.get_all_storage(self.collection), [])

        # With collection=None
        self.assertEqual(self.service.get_all_storage(None), [])

        # With items
        s1 = StorageDefinition(name="Box A", type="Box")
        self.collection.storage_definitions.append(s1)
        res = self.service.get_all_storage(self.collection)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['name'], "Box A")

    def test_get_storage(self):
        s1 = StorageDefinition(name="Box A", type="Box")
        self.collection.storage_definitions.append(s1)

        # Found
        res = self.service.get_storage(self.collection, "Box A")
        self.assertIsNotNone(res)
        self.assertEqual(res['name'], "Box A")

        # Not found
        self.assertIsNone(self.service.get_storage(self.collection, "Box B"))

        # collection=None
        self.assertIsNone(self.service.get_storage(None, "Box A"))

    def test_add_storage(self):
        # Success
        res = self.service.add_storage(self.collection, "Box A", "Box", "Desc", "path", "set")
        self.assertTrue(res)
        self.assertEqual(len(self.collection.storage_definitions), 1)
        self.assertEqual(self.collection.storage_definitions[0].name, "Box A")

        # Duplicate
        res = self.service.add_storage(self.collection, "Box A", "Box")
        self.assertFalse(res)
        self.assertEqual(len(self.collection.storage_definitions), 1)

        # collection=None
        self.assertFalse(self.service.add_storage(None, "Box B", "Box"))

    def test_update_storage(self):
        s1 = StorageDefinition(name="Box A", type="Box", description="Old", image_path="old_path", set_code="old_set")
        s2 = StorageDefinition(name="Box B", type="Box")
        self.collection.storage_definitions.extend([s1, s2])

        # Success - all fields
        res = self.service.update_storage(self.collection, "Box A", "Box A Updated", "Binder", "New Desc", "new_path", "new_set")
        self.assertTrue(res)
        self.assertEqual(s1.name, "Box A Updated")
        self.assertEqual(s1.type, "Binder")
        self.assertEqual(s1.description, "New Desc")
        self.assertEqual(s1.image_path, "new_path")
        self.assertEqual(s1.set_code, "new_set")

        # Success - same name
        res = self.service.update_storage(self.collection, "Box A Updated", "Box A Updated", "Box", "Same Name", "p", "s")
        self.assertTrue(res)
        self.assertEqual(s1.name, "Box A Updated")
        self.assertEqual(s1.description, "Same Name")

        # Failure - rename to existing
        res = self.service.update_storage(self.collection, "Box A Updated", "Box B", "Box", "D", "P", "S")
        self.assertFalse(res)
        self.assertEqual(s1.name, "Box A Updated") # Should not have changed

        # Failure - non-existent
        res = self.service.update_storage(self.collection, "Non-existent", "New", "Box", "D", "P", "S")
        self.assertFalse(res)

        # Failure - collection=None
        self.assertFalse(self.service.update_storage(None, "Box B", "New", "Box", "D", "P", "S"))

    def test_delete_storage(self):
        s1 = StorageDefinition(name="Box A", type="Box")
        self.collection.storage_definitions.append(s1)

        # Success
        res = self.service.delete_storage(self.collection, "Box A")
        self.assertTrue(res)
        self.assertEqual(len(self.collection.storage_definitions), 0)

        # Failure - non-existent
        res = self.service.delete_storage(self.collection, "Box A")
        self.assertFalse(res)

        # Failure - collection=None
        self.assertFalse(self.service.delete_storage(None, "Box B"))

if __name__ == '__main__':
    unittest.main()
