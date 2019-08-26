from backend import test, fetch_data

class TestFetchMovie(test.TestCase):
    acces_key = fetch_data.FetchMovie.access_key
    url = fetch_data.FetchMovie.url

    def test_create_fetched_url(self):
        attribute1 = 't=1234'
        answer1 = self.url+'?'+attribute1+'&'+self.acces_key
        attribute2 = 't=test&test1=test3'
        answer2 = self.url + '?' + attribute2 + '&' + self.acces_key

        self.assertEqual(answer1, fetch_data.FetchMovie.create_fetched_url(attribute1))
        self.assertEqual(answer2, fetch_data.FetchMovie.create_fetched_url(attribute2))

    def test_fetch_url(self):
        fetched_url = self.url + '?' + 't=Shrek' + '&' + self.acces_key

        description = fetch_data.FetchMovie.fetch_url(fetched_url)

        self.assertIsInstance(description, str)
        self.assertLessEqual({'Title': 'Shrek'}, description)


    def test_fetch_movie_by_title(self):
        title = 'Shrek'
        description = fetch_data.FetchMovie.fetch_movie_by_title(title)

        self.assertIsInstance(description, str)
        self.assertLessEqual({'Title': 'Shrek'}, description)

    def test_fetch_random_movies(self):
        descriptions = fetch_data.FetchMovie.fetch_random_movies(5)

        self.assertEquals(5, len(descriptions))
        self.assertIsInstance(descriptions, list)
        self.assertIsInstance(descriptions[0], str)


