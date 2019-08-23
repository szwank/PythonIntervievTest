from google.appengine.ext import ndb
from backend.keyvalue import KeyValue


class Movie(ndb.Model):
    title = ndb.StringProperty(indexed=True)
    data = ndb.KeyProperty(KeyValue, repeated=True)

    @classmethod
    def create(cls, title, data):
        data = KeyValue.create(title, data)
        entity = cls(title=title,
                     data=data)
        entity.put()
        return entity

    @classmethod
    def get(cls):
        pass


