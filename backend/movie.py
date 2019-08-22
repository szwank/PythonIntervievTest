from google.appengine.ext import ndb

class Ratings(ndb.Model):
    pass

class Movie(ndb.Model):
    title = ndb.StringProperty(indexed=True)
    plot = ndb.StringProperty(indexed=False)
    rated = ndb.StringProperty(indexed=False)
    ratings_id = ndb.KeyProperty(Ratings, repeated=True)
    dvd = ndb.StringProperty(indexed=False)
    writer = ndb.StringProperty(indexed=False)
    production = ndb.StringProperty(indexed=False)
    actors = ndb.StringProperty(indexed=False)
    type = ndb.StringProperty(indexed=False)
    imdbVotes = ndb.IntegerProperty(indexed=False)
    website = ndb.StringProperty(indexed=False)
    poster = ndb.StringProperty(indexed=False)
    director = ndb.StringProperty(indexed=False)
    released = ndb.StringProperty(indexed=False)
    awards = ndb.StringProperty(indexed=False)
    genre = ndb.StringProperty(indexed=False)
    imdbRating = ndb.FloatProperty(indexed=False)
    language = ndb.StringProperty(indexed=False)
    cauntry = ndb.StringProperty(indexed=False)
    boxOffice = ndb.StringProperty(indexed=False)
    runTime = ndb.StringProperty(indexed=False)
    imdbID = ndb.StringProperty(indexed=False)
    metascore = ndb.IntegerProperty(indexed=False)
    year = ndb.IntegerProperty(indexed=False)

    def get(self):
        pass


