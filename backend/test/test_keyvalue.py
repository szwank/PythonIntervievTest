import time

from backend import test
from backend import keyvalue


class TestCache(test.TestCase):

    def test_set(self):
        key = keyvalue.set("my_key", "my_value")
        self.assertTrue(key is not None)
        self.assertEqual(keyvalue.get("my_key"), "my_value")

        keyvalue.set("my_key", "my_value2")
        self.assertEqual(keyvalue.get("my_key"), "my_value2")

        self.assertEqual(keyvalue.get("nothing_on_this_key"), None)

    def test_namespace(self):
        keyvalue.set("my_key", "my_value", namespace="my_namespace")
        self.assertEqual(keyvalue.get("my_key", namespace="my_namespace"), "my_value")

        keyvalue.set("my_key", "my_value2", namespace="my_namespace2")
        self.assertEqual(keyvalue.get("my_key", namespace="my_namespace"), "my_value")
        self.assertEqual(keyvalue.get("my_key", namespace="my_namespace2"), "my_value2")

    def test_expires(self):
        keyvalue.set("my_key_with_expires", "my_value", expires=1)
        self.assertEqual(keyvalue.get("my_key_with_expires"), "my_value")

        time.sleep(1)

        self.assertEqual(keyvalue.get("my_key_with_expires"), None)

    def test_delete(self):
        keyvalue.set("my_key", "my_value")
        self.assertEqual(keyvalue.get("my_key"), "my_value")
        keyvalue.delete("my_key")
        self.assertEqual(keyvalue.get("my_key"), None)
