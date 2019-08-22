import datetime
import random
import logging

from google.appengine.ext import ndb

from backend.cache import lru_cache
from backend import error


class NotFound(error.Error):
    pass


class Token(ndb.Model):
    child_key = ndb.KeyProperty(indexed=False)
    expires = ndb.DateTimeProperty(indexed=False)

    @classmethod
    def create(cls, parent_key=None, child_key=None, expires=3600):
        token = "%040x" % random.getrandbits(512)

        entity = cls.get_or_insert(ndb.Key(cls, token).id(), parent=parent_key)
        if entity.expires is not None and not entity.expired():
            logging.exception("Token collision: %s" % token)
            return cls.create(parent_key, child_key, expires)

        entity.update(
            child_key=child_key,
            expires=datetime.datetime.now() + datetime.timedelta(seconds=expires)
        )

        cls._get.lru_set(entity, args=(cls, parent_key, entity.id))

        return entity

    @classmethod
    @lru_cache()
    def _get(cls, parent_key, id):
        entity = None

        try:
            entity = ndb.Key(urlsafe=id, parent=parent_key).get()
        except:
            pass

        return entity

    @classmethod
    def get(cls, parent_key, id):
        entity = cls._get(parent_key, id)

        if entity is None or not isinstance(entity, cls) or entity.expired():
            raise NotFound("Token not found")

        return entity

    @property
    def parent_key(self):
        return self.key.parent()

    def update(self, **kwargs):
        updates = [setattr(self, key, value) for key, value in kwargs.iteritems() if getattr(self, key) != value]
        if len(updates) > 0:
            self.put()
        return self

    def expired(self):
        return datetime.datetime.now() > self.expires

    def renew(self):
        self.revoke()
        return self.create(self.parent_key, self.child_key)

    def revoke(self):
        self.update(expires=datetime.datetime.now() - datetime.timedelta(seconds=1))
        self._get.lru_clear(args=[self.__class__, self.parent_key, self.id])

    @property
    def id(self):
        return self.key.urlsafe()
