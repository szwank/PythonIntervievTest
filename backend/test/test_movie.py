from backend import test, movie, fetch_data
from google.appengine.ext import ndb
import time
import json


class TestMovie(test.TestCase):

    description_without_title = {'Website': 'N/A', 'Production': 'Universal',
                                 'Actors': 'Faith Domergue, Richard Long, Marshall Thompson, Kathleen Hughes',
                                 'Metascore': 'N/A', 'Runtime': '82 min', 'imdbVotes': '837', 'Year': '1955',
                                 'Director': 'Francis D. Lyon', 'Response': 'True',
                                 'Rated': 'Approved', 'Awards': 'N/A',
                                 'DVD': '13 Apr 1994', 'Type': 'movie', 'Released': '05 Aug 1955',
                                 'Genre': 'Fantasy, Horror', 'BoxOffice': 'N/A', 'Plot':
                                     'American G.I.s who trespass on a Hindu ceremony are hunted down by a beautiful woman who has the power to transform herself into a cobra.',
                                 'Country': 'USA', 'imdbRating': '5.8', 'imdbID': 'tt0047966', 'Language': 'English'}
    title = 'Cult of the Cobra'

    wrong_format_of_description = "{'Type': 'movie', 'Released': '05 Aug 1955'}}"

    description_with_title = {'Website': 'N/A', 'Production': 'Universal',
                                 'Actors': 'Faith Domergue, Richard Long, Marshall Thompson, Kathleen Hughes',
                                 'Metascore': 'N/A', 'Runtime': '82 min', 'imdbVotes': '837', 'Year': '1955',
                                 'Director': 'Francis D. Lyon', 'Response': 'True',
                                 'Rated': 'Approved', 'Awards': 'N/A',
                                 'DVD': '13 Apr 1994', 'Type': 'movie', 'Released': '05 Aug 1955',
                                 'Genre': 'Fantasy, Horror', 'BoxOffice': 'N/A', 'Plot':
                                     'American G.I.s who trespass on a Hindu ceremony are hunted down by a beautiful woman who has the power to transform herself into a cobra.',
                                 'Country': 'USA', 'imdbRating': '5.8', 'imdbID': 'tt0047966',
                                 'Language': 'English', 'Title': 'Cult of the Cobra'}


    def test_create(self):
        obj = movie.Movie.create(title=self.title, description=self.description_without_title, put_into_database=False)
        self.assertIsNot(obj, movie.Movie.get_by_title(title=self.title))
        obj.put()
        self.assertEqual(obj, movie.Movie.get_by_ID(ID=obj.key.id()))
        self.assertTrue(obj.description == self.description_without_title)
        self.assertTrue(obj.title == self.title)
        self.assertRaises(movie.TitleTaken, lambda: movie.Movie.create(title=self.title, description=self.description_without_title))
        self.assertRaises(ValueError, lambda: movie.Movie.create(title=self.title, description=123))
        self.assertRaises(ValueError, lambda: movie.Movie.create(title=self.title, description=self.wrong_format_of_description))

    def test_create_from_description(self):

        obj = movie.Movie.create_from_decription(description=dict(self.description_with_title), put_into_database=False)
        self.assertIsNot(obj, movie.Movie.get_by_title(title=self.title))
        obj.put()
        self.assertEqual(obj, movie.Movie.get_by_ID(ID=obj.key.id()))
        self.assertTrue(obj.description == self.description_without_title)
        self.assertTrue(obj.title == self.title)
        self.assertRaises(movie.TitleTaken,
                          lambda: movie.Movie.create_from_decription(description=dict(self.description_with_title)))
        self.assertRaises(ValueError, lambda: movie.Movie.create_from_decription(description=123))
        self.assertRaises(ValueError, lambda: movie.Movie.create_from_decription(description=self.wrong_format_of_description))
        self.assertRaises(ValueError, lambda: movie.Movie.create_from_decription(description=self.description_without_title))

    def test_create_from_list_of_descriptions(self):
        self.fetch_movie_mock.set_description(description=self.description_with_title)
        descriptions = fetch_data.FetchMovie.fetch_random_movies(10)

        objects = movie.Movie.create_from_list_of_descriptions(descriptions)
        self.assertEqual(len(objects), 10)
        self.assertListEqual(objects, map(lambda obj: movie.Movie.get_by_ID(ID=obj.key.id()), objects))

    def test_add_movies_to_database(self):
        self.fetch_movie_mock.set_description(description=self.description_with_title)
        objects = movie.Movie.add_movies_to_database(10)

        self.assertEqual(len(objects), 10)
        self.assertListEqual(objects, map(lambda obj: movie.Movie.get_by_ID(ID=obj.key.id()), objects))

    def test_delete_by_ID(self):
        obj = movie.Movie.create_from_decription(self.description_with_title)

        self.assertIsNone(movie.Movie.delete_by_ID(obj.key.id()))
        self.assertIsNone(movie.Movie.get_by_ID(obj.key.id()))


    def test_delete_all_movies(self):
        self.fetch_movie_mock.set_description(description=self.description_with_title)
        objects = movie.Movie.add_movies_to_database(10)

        map(lambda obj: movie.Movie.delete_by_ID(obj.key.id()), objects)
        self.assertEquals(map(lambda obj: movie.Movie.get_by_ID(ID=obj.key.id()), objects), [None]*10)

    def test_get_by_ID(self):
        obj = movie.Movie.create_from_decription(self.description_with_title)

        taken_obj = movie.Movie.get_by_ID(obj.key.id())

        self.assertTrue(obj.title == taken_obj.title)
        self.assertEqual(obj.key.id(), taken_obj.key.id())
        self.assertTrue(obj.description == taken_obj.description)

        movie.Movie.delete_by_ID(obj.key.id())

        self.assertIsNone(movie.Movie.get_by_ID(obj.key.id()))



