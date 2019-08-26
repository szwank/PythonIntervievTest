from backend import test, movie

class TestMovie(test.TestCase):

    def test_create(self):
        description_without_title = "{'Website': 'N/A', 'Production': 'Universal', 'Actors': 'Faith Domergue, Richard Long, Marshall Thompson, Kathleen Hughes', \
              'Metascore': 'N/A', 'Runtime': '82 min', 'imdbVotes': '837', 'Year': '1955', 'Director': 'Francis D. Lyon', 'Response': 'True', \
              'Rated': 'Approved', 'Awards': 'N/A', \
              'DVD': '13 Apr 1994', 'Type': 'movie', 'Released': '05 Aug 1955', \
              'Genre': 'Fantasy, Horror', 'BoxOffice': 'N/A', 'Plot': \
              'American G.I.s who trespass on a Hindu ceremony are hunted down by a beautiful woman who has the power to transform herself into a cobra.', \
              'Country': 'USA', 'imdbRating': '5.8', 'imdbID': 'tt0047966', 'Language': 'English'}"

        obj = movie.Movie.create(title='Cult of the Cobra', description=description_without_title, put_into_database=False)
        self.a