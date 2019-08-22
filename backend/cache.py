# pylint: disable=W0102,W0633
import time
import functools

from collections import OrderedDict
from thread import allocate_lock

from google.appengine.api import memcache


__LIST_SET = (list, set)
__LRU_DECORATORS = []

def lru_clear_all():
    """
    Clears all lru decorators
    """
    for func in __LRU_DECORATORS:
        func.lru_clear_all()

def lru_cache(max_size=1000, expires=3600):  # noqa: max-complexity=12
    """
    Least-recently used cache decorator.
    """
    def decorator(func):
        size, hits, misses = 0, 1, 2
        stats = [0, 0, 0]
        cache = OrderedDict()  # order: least recent to most recent
        cache_popitem = cache.popitem
        cache_pop = cache.pop
        lock = allocate_lock()

        def lru_clear_all():
            with lock:
                cache.clear()
                stats[size] = 0
                stats[hits] = 0
                stats[misses] = 0

        def lru_clear(args=[], kwargs={}):
            key = lru_key(*args, **kwargs)

            with lock:
                if key in cache:
                    cache_pop(key)

        def lru_set(value, args=[], kwargs={}):
            now = time.time()
            key = lru_key(*args, **kwargs)

            with lock:
                if key in cache:
                    cache_pop(key)
                elif stats[size] == max_size:
                    cache_popitem(0)
                else:
                    stats[size] += 1
                cache[key] = value, now

        def lru_key(*args, **kwargs):
            items = [tuple(arg) if isinstance(arg, __LIST_SET) else arg for arg in args]

            if kwargs:
                items += ['|'] + [tuple([kwarg[0], tuple(kwarg[1])]) if isinstance(kwarg[1], __LIST_SET) else kwarg for kwarg in sorted(kwargs.items())]

            return hash(tuple(items))

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            key = lru_key(*args, **kwargs)

            with lock:
                if key in cache:
                    value, timestamp = cache_pop(key)
                    if timestamp + expires > now:
                        stats[hits] += 1
                        cache[key] = value, now  # record recent use of this key
                        return value
                    else:
                        stats[size] -= 1

            value = func(*args, **kwargs)
            stats[misses] += 1

            with lock:
                if stats[size] == max_size:
                    cache_popitem(0)  # purge least recently used cache entry
                else:
                    stats[size] += 1
                cache[key] = value, now  # record recent use of this key
                return value

        wrapper.lru_size = lambda: stats[size]
        wrapper.lru_hits = lambda: stats[hits]
        wrapper.lru_misses = lambda: stats[misses]
        wrapper.lru_clear_all = lru_clear_all
        wrapper.lru_clear = lru_clear
        wrapper.lru_set = lru_set
        __LRU_DECORATORS.append(wrapper)
        return wrapper
    return decorator

def mem_cache(expires=604800):  # noqa: max-complexity=12
    """
    Memcache cache decorator.
    We rely on __repr__() for generating memcache keys from args and kwargs,
    therefore its required that __repr__() is overloaded on all classes that
    use mem_cache. __repr__() should return a string that is unique for that
    class or instance.
    604800 = 7 * 24 * 60 * 60
    """
    def decorator(func):
        hits, misses = 0, 1
        stats = [0, 0]
        func.__mem_cache_name__ = None
        memcache_set = memcache.set  # @UndefinedVariable
        memcache_get = memcache.get  # @UndefinedVariable

        def mem_set(value, args=(), kwargs={}):
            key = mem_key(*args, **kwargs)
            memcache_set(key, value, time=expires, namespace="mem_cache")

        def mem_key(*args, **kwargs):
            if func.__mem_cache_name__ is None:
                argnames = func.func_code.co_varnames[:func.func_code.co_argcount]

                if argnames and argnames[0] == "cls":  # classmethod. note: a function could have cls as first argument...
                    func.__mem_cache_name__ = "c:%s:%s" % (args[0].__name__, func.__name__)
                elif argnames and argnames[0] == "self":  # instance method
                    func.__mem_cache_name__ = "i:%s:%s" % (repr(args[0]), func.__name__)
                else:  # function
                    func.__mem_cache_name__ = "f:%s:%s" % (func.__module__, func.__name__)

            start = 0 if func.__mem_cache_name__[0] == "f" else 1

            items = [repr(arg) for arg in args[start:]]

            if kwargs:
                items += ['|'] + [tuple([kwarg[0], repr(kwarg[1])]) for kwarg in sorted(kwargs.items())]

            key = ':'.join([func.__mem_cache_name__] + items)

            if "instance at" in key or "object at" in key:
                raise Exception('mem_key contains memory address, overload __repr__(). __mem_cache_name__: %s, mem_key: %s' % (func.__mem_cache_name__, key))

            return key

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = mem_key(*args, **kwargs)

            value = memcache_get(key, namespace="mem_cache")
            if value:
                stats[hits] += 1
                return value

            stats[misses] += 1
            value = func(*args, **kwargs)
            memcache_set(key, value, time=expires, namespace="mem_cache")

            return value

        wrapper.mem_hits = lambda: stats[hits]
        wrapper.mem_misses = lambda: stats[misses]
        wrapper.mem_set = mem_set
        return wrapper
    return decorator
