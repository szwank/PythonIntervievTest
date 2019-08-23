from google.appengine.ext import ndb
from backend.keyvalue import KeyValue, Key
from backend import fetch_data
import logging

Empty = []

class Movie(KeyValue):

    @classmethod
    def initialize_movie_database(cls, how_much_to_add):
        # if cls.query(Movie).fetch(1) is not None:
        if cls.query().fetch(1) == Empty:
            # logging.error(cls.query().fetch(1))
            fetch_data.FetchMovie.add_many_movies_to_database(how_much_to_add=how_much_to_add)

        else:
            # Movies are in database no need for adding them
            logging.info("Movies are still in data base. None was added")
            pass

    @classmethod
    def delete_all_movies(cls):
        list_of_keys = ndb.put_multi(cls.query())
        list_of_entities = ndb.get_multi(list_of_keys)
        ndb.delete_multi(list_of_keys)



