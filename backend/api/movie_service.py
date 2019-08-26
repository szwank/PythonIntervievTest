from backend import api
from protorpc import remote, messages, message_types
from backend import movie, fetch_data, error
from backend.oauth2 import oauth2


from google.appengine.datastore.datastore_query import Cursor

class UnknownDirection(error.Error):
    pass

class NoPageLeftInThatDirection(error.Error):
    pass

class JsonField(messages.StringField):
    type = dict


class GetTitle(messages.Message):
    get = messages.StringField(1, required=True)


class Title(messages.Message):
    title = messages.StringField(1, required=True)


class Titles(messages.Message):
    titles = messages.MessageField(Title, 1, repeated=True)


class MessageCursors(messages.Message):
    next_cursor = messages.StringField(1, default="")
    current_cursor = messages.StringField(2, default="")


class GetMoviesRequest(messages.Message):
    how_many_on_page = messages.IntegerField(1, default=10)
    message_cursors = messages.MessageField(MessageCursors, 2)

    class Order(messages.Enum):
        TITLE = 1

    order = messages.EnumField(Order, 3, default=Order.TITLE)

    class Dirction(messages.Enum):
        NEXT = 1
        PREVIOUS = 2

    direction = messages.EnumField(Dirction, 4, default=Dirction.NEXT)


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


class GetMoviesRespond(messages.Message):
    movies = messages.MessageField(Movie, 1, repeated=True)
    message_cursors = messages.MessageField(MessageCursors, 2, required=True)
    more_to_get = messages.BooleanField(3, required=True)


@api.endpoint(path="movie", title="Movie API")
class MovieService(remote.Service):

    @remote.method(GetMoviesRequest, GetMoviesRespond)
    def get_movies(self, request):
        query = movie.Movie.query()

        if request.order == GetMoviesRequest.Order.TITLE:
            query = query.order(movie.Movie.title)


        if request.direction == request.direction.NEXT:
            if request.message_cursors:     # usual_case
                cursor = Cursor(urlsafe=request.cursor.next_cursor)
                current_cursor = request.cursor.next_cursor
            else:   # No Cursors. First batch
                cursor = Cursor()
                current_cursor = cursor.urlsafe()

            movies, next_cursor, more = query.fetch_page(request.how_many_on_page, start_cursor=cursor)
            next_cursor = next_cursor.urlsafe()

        elif request.direction == request.direction.PREVIOUS:
            if request.cursor.current_cursor:       # We are at first batch cursor- there is no data to get in this direction.
                raise NoPageLeftInThatDirection("Cannot get more in that direction.")

            cursor = Cursor(urlsafe=request.cursor.current_cursor)
            cursor.reversed()

            movies, next_cursor, more = query.fetch_page(request.how_many_on_page, start_cursor=cursor)

            movies.reverse()  # There are in reversed order- need to reverse
            current_cursor = next_cursor.reversed().urlsafe()
            next_cursor = cursor.reversed().urlsafe()
        else:
            raise UnknownDirection("Direction %s is unknown. % request.direction")

        map_to_movie = lambda item: Movie(title=item.title,
                                          ID=item.key.id(),
                                          description=item.description)

        movies = map(map_to_movie, movies)
        message_cursors = MessageCursors(next_cursor=next_cursor, current_cursor=current_cursor)
        return GetMoviesRespond(movies=movies, message_cursors=message_cursors, more_to_get=more)

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



