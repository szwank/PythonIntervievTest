# pylint: disable=W0102,W0633
import datetime
import json
import hashlib

from google.appengine.ext import ndb

from backend.cache import lru_cache, mem_cache


class Key(object):
    def __new__(cls, key, namespace=None):
        return hashlib.md5("%s|%s" % (namespace, key)).hexdigest()


class KeyValue(ndb.Model):
    """
    Key-value store using ndb.
    Stores any json serializable value on a unique key.
    If the key already exists the value will be overwritten
    """
    value = ndb.StringProperty(indexed=False)
    expires = ndb.DateTimeProperty(indexed=False)

    @classmethod
    def create(cls, key, value, expires=None):
        entity = cls.get_or_insert(ndb.Key(cls, key).id())

        entity.update(
            value=value,
            expires=datetime.datetime.now() + datetime.timedelta(seconds=expires) if expires is not None else None
        )

        cls.get.lru_set(entity, args=[cls, key])
        return entity

    def update(self, **kwargs):
        updates = [setattr(self, key, value) for key, value in kwargs.iteritems() if getattr(self, key) != value]
        if len(updates) > 0:
            self.put()
        return self

    def delete(self):
        self.update(expires=datetime.datetime.now() - datetime.timedelta(seconds=1))
        self.key.delete_async()

    @classmethod
    @lru_cache()
    @mem_cache()
    def get(cls, key):
        return ndb.Key(cls, key).get()

    def expired(self):
        return self.expires is not None and datetime.datetime.now() > self.expires


def set(key, value, namespace=None, expires=None):
    key = Key(key, namespace=namespace)
    entity = KeyValue.create(key, json.dumps(value), expires)
    return key if entity is not None else None

def get(key, namespace=None):
    key = Key(key, namespace=namespace)
    entity = KeyValue.get(key)
    return json.loads(entity.value) if entity and not entity.expired() else None

def delete(key, namespace=None):
    key = Key(key, namespace=namespace)
    entity = KeyValue.get(key)
    if entity:
        entity.delete()
