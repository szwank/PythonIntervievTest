from backend import api
from protorpc import remote, messages, message_types
from backend import movie
import json

class GetTitle(messages.Message):
    get = messages.StringField(1, required=True)

class Title(messages.Message):
    title = messages.StringField(1, required=True)

class Titles(messages.Message):
    titles = messages.MessageField(Title, 1, repeated=True)

class GetMoviesRequest(messages.Message):
    how_many = messages.IntegerField(1, default=10)

    class Order(messages.Enum):
        TITLE = 1

    order = messages.EnumField(Order, 3, default=Order.TITLE)

class GetSingleMovieRequest(messages.Message):
    title = messages.StringField(1, required=True)

class Movie(messages.Message):
    movie = messages.StringField(1, required=True)

class Movies(messages.Message):
    movies = messages.MessageField(Movie, 1, repeated=True)


# class Title(messages.Message):
#     title = message
#
@api.endpoint(path="movie", title="Movie API")
class MovieService(remote.Service):

    @remote.method(GetMoviesRequest, Movies)
    def get_movies(self, request):
        query = movie.Movie.query()

        if request.order == GetMoviesRequest.Order.TITLE:
            query = query.order(movie.Movie.title)

        movies = map(lambda result: Movie(movie=str(json.loads(result.value))), query.fetch(request.how_many))

        return Movies(movies=movies)

    @remote.method(GetSingleMovieRequest, Movie)
    def get_movie(self, request):
        query = movie.Movie.query()





