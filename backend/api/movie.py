from backend import api
from backend import movie
from protorpc import remote, messages, message_types


class GetTitle(messages.Message):
    get = messages.StringField(1, required=True)

class Titles(messages.Message):
    titles = messages.StringField(1, required=True)

@api.endpoint(path="title", title="Movie API")
class Titles(remote.Service):
    @remote.method(GetTitle, Titles)
    def get(self, reguest):
        titles = movie.Movie.get_titles
        Titles(titles=titles)
        return Titles




