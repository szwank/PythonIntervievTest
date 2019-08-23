from google.appengine.api import urlfetch
from backend import error
import logging
from google.appengine.ext import webapp

class ErrorWhileFetching(error.Error):
    pass

class FetchMovie:
    access_key = 'apikey=ffdb4910'
    url = 'http://www.omdbapi.com/'

    def __init__(self):
        pass

    @classmethod
    def fetch_movie(cls, *args):
        url_attributes = "&".join(args)
        try:
            fetched_url = cls.url + '?' + url_attributes + '&' + cls.access_key
            result = urlfetch.fetch(fetched_url)

            if result.status_code == 200:
                return result.content
            else:
                logging.error(result.status_code)
        except:
            raise ErrorWhileFetching("While fetching %s error was occur" % fetched_url)

    @classmethod
    def add_movie_to_database(cls):
        pass

    def __initialize_movies_data_base(self):
        pass

    def find_movie_by_name(self, name):
        pass

# class Print(webapp.RequestHandler):
#     def get(self):
#         self.response.header['Content-type'] = 'text/plain'
#         self.response.write('hello')



