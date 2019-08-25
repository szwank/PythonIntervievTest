from google.appengine.api import urlfetch
from backend import error
import logging



class ErrorWhileFetching(error.Error):
    pass


class MoviesAreInDataBase(error.Error):
    pass


class FetchMovie:
    access_key = 'apikey=ffdb4910'
    url = 'http://www.omdbapi.com/'

    @classmethod
    def create_fetched_url(cls, url_attributes):
        return '%s?%s&%s' % (cls.url, url_attributes, cls.access_key)

    @classmethod
    def fetch_url(cls, fetched_url):
        try:
            result = urlfetch.fetch(fetched_url)

            if result.status_code == 200:
                return result.content
            else:
                logging.error(result.status_code)
        except:
            raise ErrorWhileFetching("While fetching %s error was occur" % fetched_url)

    @classmethod
    def fetch_movie(cls, *args):
        url_attributes = "&".join(args)
        fetched_url = cls.create_fetched_url(url_attributes)
        return cls.fetch_url(fetched_url)

    @classmethod
    def fetch_movie_by_title(cls, movie_title):
        cls.fetch_movie('t= %s' % movie_title)
        









