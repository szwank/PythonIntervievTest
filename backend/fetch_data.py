from google.appengine.api import urlfetch
from backend import error
import logging
import random
import json
import movie


class ErrorWhileFetching(error.Error):
    pass

class MoviesAreInDataBase(error.Error):
    pass

class FetchMovie:
    access_key = 'apikey=ffdb4910'
    url = 'http://www.omdbapi.com/'

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
    def add_many_movies_to_database(cls, how_much_to_add):
        movies_id_to_fetch = random.sample(range(70000), how_much_to_add)
        for i in range(how_much_to_add):
            argument = 'i=tt' + "%07d" % movies_id_to_fetch[i]
            result = cls.fetch_movie(argument)
            cls.add_movie_to_database(data=result)

    def __initialize_movies_data_base(self):
        pass

    @classmethod
    def add_movie_to_database(self, data):
        data_dictionary = json.loads(data)
        title = data_dictionary.get('Title', 'No title')
        movie.Movie.create(title, data)



    def find_movie_by_name(self, name):
        pass


# class Print(webapp.RequestHandler):
#     def get(self):
#         self.response.header['Content-type'] = 'text/plain'
#         self.response.write('hello')



