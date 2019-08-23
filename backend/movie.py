from google.appengine.ext import ndb
from backend.keyvalue import KeyValue
import logging

class Movie(ndb.Model):
    title = ndb.StringProperty(indexed=True)
    data = ndb.KeyProperty(KeyValue)

    @classmethod
    def create(cls, title, data):
        data = KeyValue.create(title, data)
        entity = cls(title=title,
                     data=data.key)
        entity.put()
        logging.error('done')
        # return entity

    @classmethod
    def get(cls):
        pass


