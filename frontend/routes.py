from google.appengine.ext import webapp
from backend.fetch_data import FetchMovie
import json
import logging
from backend import movie
from backend import keyvalue


class Index(webapp.RequestHandler):
    def get(self):

        # data = FetchMovie.fetch_movie('t=cat')
        # self.response.write(data)
        # data = json.loads(data)
        # keyvalue.set('kot', data)
        # # movie.Movie.create(data)
        respond = movie.Movie.get_titles()
        self.response.write(respond)

        # entity = movie.set(data)
        # result = movie.get('Black Cat, White Cat')
        # self.response.write(result.get('Title'))
        # movie.Movie.create('shrek', '{1: 2}')
        # keyvalue.KeyValue.create(data_dictionary.get('Title', 'No title'), data)
        # logging.error(data.content)

class Delete_all_movies(webapp.RequestHandler):
    def get(self):

        movie.Movie.delete_all_movies()
        self.response.write('Movies removed')






