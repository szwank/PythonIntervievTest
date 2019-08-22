from google.appengine.ext import ndb

context = ndb.get_context()
context.set_cache_policy(lambda key: False)
context.set_memcache_policy(lambda key: False)
