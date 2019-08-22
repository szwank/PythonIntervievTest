from backend import test, environment


class TestEnvironment(test.TestCase):

    def test_environment(self):
        self.assertEqual(environment.get_application_id(), "testbed-test")
        self.assertEqual(environment.get_default_gcs_bucket_name(), "app_default_bucket")
        self.assertEqual(environment.get_default_version_hostname(), None)

        self.assertTrue(environment.DEV_APPSERVER)
        self.assertTrue(environment.TEST)
        self.assertTrue(environment.URL)
        self.assertTrue(environment.CLOUD_STORAGE_BUCKET)
        self.assertTrue(environment.CLOUD_STORAGE_URL)
