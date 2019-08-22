import logging
import unittest
import json
import StringIO
import urlparse

try:
    from google.appengine.ext import testbed
    from google.appengine.datastore import datastore_stub_util
    from google.appengine.ext import ndb
except ImportError:
    testbed = None

from backend.cache import lru_clear_all
from backend import environment


logging.getLogger().setLevel(logging.WARN)


class TestCase(unittest.TestCase):

    def setUp(self):
        environment.TEST = True

        lru_clear_all()

        if testbed:
            self.testbed = testbed.Testbed()
            self.testbed.setup_env(current_version_id='testbed.version')
            self.testbed.activate()

            # init stubs
            self.testbed.init_logservice_stub()
            self.testbed.init_memcache_stub()
            self.testbed.init_app_identity_stub()
            self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=0)
            self.testbed.init_datastore_v3_stub(consistency_policy=self.policy)
            self.testbed.init_blobstore_stub()
            self.testbed.init_mail_stub()

            # get stubs
            self.task_queue_stub = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)
            self.mail_stub = self.testbed.get_stub(testbed.MAIL_SERVICE_NAME)

            # disable ndb cache
            context = ndb.get_context()
            context.set_cache_policy(lambda key: False)
            context.set_memcache_policy(lambda key: False)

        # api mock
        self.api_mock = ApiMock()

    def tearDown(self):
        if testbed:
            self.testbed.deactivate()


class ApiMock(object):
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.expires = None
        self._status_code = None

    def _start_response(self, status_code, headers):
        self._status_code = status_code

    def _request(self, url, method='POST', data={}, headers=[]):
        import backend.api

        url = urlparse.urlparse(url)

        env = dict(
            QUERY_STRING=url.query,
            REQUEST_METHOD=method,
            PATH_INFO=url.path
        )

        if method == 'POST':
            content = json.dumps(data)
            env['wsgi.input'] = StringIO.StringIO(content)
            env['CONTENT_LENGTH'] = len(content)

        resp = backend.api.application(env, self._start_response)[0]

        try:
            body = json.loads(resp)

            if set(["access_token", "refresh_token", "expires"]) == set(body.keys()):
                self.access_token = body.get("access_token")
                self.refresh_token = body.get("refresh_token")
                self.expires = body.get("expires")

        except ValueError:
            body = {"error_message": resp.strip()}
        if self._status_code != '200 OK':
            body = {"error": dict(code=self._status_code, error_name=body.get("error_name"), message=body.get("error_message"))}
        return body

    def post(self, url, data={}, access_token=None):
        return self._request(
            "%s%sauthorization=%s" % (url, "&" if "?" in url else "?", access_token or self.access_token),
            method="POST",
            data=data
        )
