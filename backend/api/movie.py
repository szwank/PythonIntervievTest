from backend import api
from protorpc import remote, messages, message_types
from backend import movie
import json

class JsonField(messages.StringField):
    type = dict

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
    movie = JsonField(1, required=True)

class Movies(messages.Message):
    movies = messages.MessageField(Movie, 1, repeated=True)


# class Title(messages.Message):
#     title = message
#
@api.endpoint(path="movie", title="Movie API")
class MovieService(remote.Service):

    @remote.method(GetMoviesRequest, Movies)
    def get_movies(self, request):
        movies = movie.get_movies(10)

        if request.order == GetMoviesRequest.Order.TITLE:
            movies.sort(key=lambda item: item.get("Title"))

        # movies = map(lambda result: Movie(movie=str(json.loads(result.value))), query.fetch(request.how_many))
        movies = map(lambda element: Movie(movie=element), movies)
        return Movies(movies=movies)

    @remote.method(GetSingleMovieRequest, Movie)
    def get_movie(self, request):
        result = movie.get(request.title)

        if result:
            return Movie(movie=result)





