import datetime

from google.appengine.ext import ndb

from backend import test, token


class TestToken(test.TestCase):

    def test_create(self):
        t = token.Token.create(ndb.Key("Parent", 1), ndb.Key("Child", 1))
        self.assertEqual(t, token.Token.get(ndb.Key("Parent", 1), t.id))
        self.assertEqual(t.parent_key, ndb.Key("Parent", 1))
        self.assertEqual(t.child_key, ndb.Key("Child", 1))
        t = token.Token.create(None, ndb.Key("Child", 1))
        self.assertEqual(t, token.Token.get(None, t.id))

        self.assertRaises(token.NotFound, lambda: token.Token.get(None, "this_should_fail"))

    def test_expire(self):
        t = token.Token.create(ndb.Key("Parent", 1), ndb.Key("Child", 1))
        self.assertTrue(t.expires > datetime.datetime.now())
        t.revoke()
        self.assertTrue(t.expired())

    def test_renew(self):
        t = token.Token.create(ndb.Key("Parent", 1), ndb.Key("Child", 1))
        new_t = t.renew()
        self.assertNotEqual(new_t, t)
        self.assertTrue(new_t.expires > t.expires)
