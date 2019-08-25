from google.appengine.ext import ndb
import random
from backend import keyvalue
from backend import fetch_data
import logging
import json

from backend.cache import lru_cache, mem_cache

Empty = []

class Movie(keyvalue.KeyValue):
    title = ndb.StringProperty(indexed=True)

    @classmethod
    def create(cls, key, title, value, expires=None):
        entity = super(cls, Movie).create(key, value, expires)
        entity.update(title=title)
        return entity

    @classmethod
    def add_movies_to_database(cls, how_much_to_add):
        movies_id_to_fetch = random.sample(range(70000), how_much_to_add)
        for i in range(how_much_to_add):
            argument = 'i=tt' + "%07d" % movies_id_to_fetch[i]
            result = fetch_data.FetchMovie.fetch_movie(argument)
            set(result)

    @classmethod
    def initialize_movie_database(cls, how_much_to_add):
        if cls.query().fetch(1) == Empty:
            cls.add_movies_to_database(how_much_to_add=how_much_to_add)
        else:
            # Movies are in database no need for adding them
            logging.info("Movies are still in data base. None was added")


    @classmethod
    def delete_all_movies(cls):
        list_of_keys = ndb.put_multi(cls.query())
        list_of_entities = ndb.get_multi(list_of_keys)
        ndb.delete_multi(list_of_entities)

    @classmethod
    # @lru_cache()
    # @mem_cache()
    def get_titles(cls, titles_on_single_page=10):
        list_of_titles = map(lambda x: str(x.title), cls.query().fetch(titles_on_single_page))
        list_of_titles.sort()
        titles = ", ".join(list_of_titles)
        return titles


    @classmethod
    def find_movie_by_name(cls, name):
        pass




def set(value, namespace=None, expires=None):
    if type(value) is str:
        value = json.loads(value)
    elif type(value) is dict:
        # Correct data, do nothing
        pass
    else:
        raise ValueError("Incorrect data")

    title = value.get("Title", "Not named")
    key = keyvalue.Key(title, namespace=namespace)
    entity = Movie.create(key, title, json.dumps(value), expires)
    return key if entity is not None else None

def get(title, namespace=None):
    key = keyvalue.Key(title, namespace=namespace)
    entity = Movie.get(key)
    return json.loads(entity.value) if entity and not entity.expired() else None

def delete(title, namespace=None):
    key = keyvalue.Key(title, namespace=namespace)
    entity = Movie.get(key)
    if entity:
        entity.delete()


