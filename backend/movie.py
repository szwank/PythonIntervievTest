from google.appengine.ext import ndb

from backend import error, fetch_data
import logging
import json


Empty = []

class TitleTaken(error.Error):
    pass


class Movie(ndb.Model):
    title = ndb.StringProperty(indexed=True)
    description = ndb.JsonProperty()

    @classmethod
    def create(cls, title, description, put_into_database=True):
        description = cls.__convert_to_json(description)

        if cls.get_by_title(title) in [Empty, None]:
            cls.__remove_title_from_description(description)        # formating data
            entity = Movie(title=title, description=description)
            if put_into_database is True:
                entity.put()
        else:
            raise TitleTaken("Movie with %s is already in database" % title)

        return entity

    @classmethod
    def __convert_to_json(cls, description):
        if type(description) is not dict:
            if type(description) in [unicode, str]:
                try:
                    description = json.loads(description)
                except:
                    raise ValueError('Cannot convert %s' % str(type(description)))
            else:
                raise ValueError('Unsupported format of description.')
        return description

    @classmethod
    def create_from_decription(cls, description, put_into_database=True):
        description = cls.__convert_to_json(description)

        try:
            title = description['Title']
        except:
            raise ValueError("No title in description.")

        cls.__remove_title_from_description(description)

        return cls.create(title, description, put_into_database)

    @classmethod
    def create_from_list_of_descriptions(cls, descriptions):
        movies = map(lambda description: cls.create_from_decription(description, put_into_database=False), descriptions)
        ndb.put_multi(movies)
        return movies if movies else None

    @classmethod
    def __remove_title_from_description(cls, description):
        try:
            del description['Title']
        except:
            pass

    @classmethod
    def add_movies_to_database(cls, how_much_to_add):
        descriptions = fetch_data.FetchMovie.fetch_random_movies(how_much_to_add)
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

    # @classmethod
    # def get_movies(cls, how_much):
    #     result = cls.query().fetch(how_much)
    #     return result if result else None


    @classmethod
    def get_by_title(cls, title):
        entity = cls.query(cls.title == title).get()
        return entity if entity else None

    @classmethod
    def get_by_ID(cls, ID):
        entity = ndb.Key(cls, ID).get()
        return entity if entity else None

    @classmethod
    def delete_by_ID(cls, ID):
        entity = cls.get_by_ID(ID)
        return entity.key.delete() if entity else None    # return always None






