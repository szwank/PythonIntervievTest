from backend import api
from protorpc import remote, messages, message_types
from backend import movie, fetch_data
from backend.oauth2 import oauth2


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
    title = messages.StringField(1, required=True)
    ID = messages.IntegerField(2, required=True)
    description = JsonField(3, required=True)


class Movies(messages.Message):
    movies = messages.MessageField(Movie, 1, repeated=True)


class AddMovieRequest(messages.Message):
    title = messages.StringField(1, required=True)


class RemoveMovieByTitleRequest(messages.Message):
    ID = messages.IntegerField(1, required=True)


@api.endpoint(path="movie", title="Movie API")
class MovieService(remote.Service):

    @remote.method(GetMoviesRequest, Movies)
    def get_movies(self, request):
        movies = movie.Movie.get_movies(request.how_many)

        if request.order == GetMoviesRequest.Order.TITLE:
            movies.sort(key=lambda item: item.description.get("Title"))

        map_to_movie = lambda item: Movie(title=item.title,
                                          ID=item.key.id(),
                                          description=item.description)

        movies = map(map_to_movie, movies)
        return Movies(movies=movies)

    @remote.method(GetSingleMovieRequest, Movie)
    def get_movie_by_title(self, request):
        result = movie.Movie.get_by_title(request.title)

        if result:
            return Movie(title=result.title, ID=result.key.id(), description=result.description)
        else:
            return Movie(movie={'No Results': 'There is no matching title'})

    @remote.method(AddMovieRequest, message_types.VoidMessage)
    def add_movie(self, request):
        movie_description = fetch_data.FetchMovie.fetch_movie_by_title(request.title)
        movie.Movie.create_from_decription(movie_description)
        return message_types.VoidMessage()

    @remote.method(RemoveMovieByTitleRequest, message_types.VoidMessage)
    @oauth2.required()
    def remove_movie_by_ID(self, request):
        movie.Movie.delete_by_ID(request.ID)
        return message_types.VoidMessage()



