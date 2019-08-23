from google.appengine.ext import webapp
from backend.fetch_data import FetchMovie
import logging
from backend import movie

class Index(webapp.RequestHandler):
    def get(self):

        data = FetchMovie.fetch_movie(FetchMovie(), 't=shrek')
        # movie.Movie.create(data.get('Title', 'No title'), data)
        # logging.error(data.content)
        self.response.write(data)






