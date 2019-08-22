# coding: utf8
import os

try:
    from google.appengine.api import app_identity
except ImportError:
    app_identity = None


def get_application_id():
    try:
        return app_identity.get_application_id()
    except AttributeError:
        return os.getenv("PROJECT_ID")

def get_default_version_hostname():
    try:
        return app_identity.get_default_version_hostname()
    except AttributeError:
        pass

def get_default_gcs_bucket_name():
    try:
        return app_identity.get_default_gcs_bucket_name()
    except AttributeError:
        pass


DEV_APPSERVER = not os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/')
TEST = False

SENDER = "<noreply@%s.appspotmail.com>" % get_application_id()

if DEV_APPSERVER:
    URL = "http://localhost:7070"
    CLOUD_STORAGE_BUCKET = "bucket"
    CLOUD_STORAGE_URL = "http://localhost:7070/_ah/gcs"
else:
    URL = "https://%s" % get_default_version_hostname()
    CLOUD_STORAGE_BUCKET = get_default_gcs_bucket_name()
    CLOUD_STORAGE_URL = "https://storage-download.googleapis.com"
