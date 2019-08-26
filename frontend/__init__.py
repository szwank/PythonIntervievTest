from google.appengine.ext import webapp
from routes import Index, Delete_all_movies

app = webapp.WSGIApplication([('/index', Index),
                              ('/delete', Delete_all_movies)
                              ], debug=True)

