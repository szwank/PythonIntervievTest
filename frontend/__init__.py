from google.appengine.ext import webapp
from routes import Index

app = webapp.WSGIApplication([('/index', Index)
                              ], debug=True)

