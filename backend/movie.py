from google.appengine.ext import ndb
import random
from backend import keyvalue, error, fetch_data
import logging
import json

from backend.cache import lru_cache, mem_cache

Empty = []

class TitleTaken(error.Error):
    pass


class Movie(ndb.Model):
    title = ndb.StringProperty(indexed=True)
    description = ndb.StringProperty()

    @classmethod
    def create(cls, title, description, put_into_database=True):
        if cls.get_by_title(title) in [Empty, None]:
            cls.__remove_title_from_description(description)        # formating data
            entity = Movie(title=title, description=json.dumps(description))
            if put_into_database is True:
                entity.put()
        else:
            raise TitleTaken("Movie with %s is already in database" % title)

        return entity

    @classmethod
    def create_from_decription(cls, description, put_into_database=True):
        if type(description) in [str, unicode]:
            description = json.loads(description)
        elif type(description) is dict:
            # Correct data, nothing to do
            pass
        else:
            raise ValueError("Incorrect data. Description needs to be str, unicode or dictionary.")

        try:
            title = description['Title']
        except:
            raise ValueError("No title in description.")

        cls.__remove_title_from_description(description)

        return cls.create(title, description, put_into_database)

    @classmethod
    def create_from_list_of_descriptions(cls, descriptions):
        movies = map(lambda description: cls.create_from_decription(description, put_into_database=False), descriptions)
        return ndb.put_multi(movies) if movies else None

    @classmethod
    def __remove_title_from_description(cls, description):
        try:
            del description['Title']
        except:
            pass

    @classmethod
    def add_movies_to_database(cls, how_much_to_add):
        descriptions = []

        movies_id_to_fetch = random.sample(range(70000), how_much_to_add)
        for i in range(how_much_to_add):
            argument = 'i=tt' + "%07d" % movies_id_to_fetch[i]
            descriptions.append(fetch_data.FetchMovie.fetch_movie(argument))
        return cls.create_from_list_of_descriptions(descriptions)


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
    def get_titles(cls, titles_on_single_page=10):
        list_of_titles = map(lambda x: str(x.title), cls.query().fetch(titles_on_single_page))
        list_of_titles.sort()
        titles = ", ".join(list_of_titles)
        return titles

    @classmethod
    def get_movies(cls, how_much):
        result = cls.query().fetch(how_much)
        return map(lambda movie: json.loads(movie.description), result) if result else None


    @classmethod
    @lru_cache()
    @mem_cache()
    def get_by_title(cls, title):
        entity = cls.query(cls.title == title).get()
        return entity if entity else None








def delete(title, namespace=None):
    key = keyvalue.Key(title, namespace=namespace)
    entity = Movie.get(key)
    if entity:
        entity.delete()




