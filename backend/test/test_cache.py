import time
import uuid

from backend import test
from backend.cache import lru_cache, mem_cache, lru_clear_all


class TestCache(test.TestCase):

    def test_lru(self):
        @lru_cache()
        def func(*args, **kwargs):
            return args, kwargs, uuid.uuid4()

        class Cls(object):
            @classmethod
            @lru_cache()
            def cls_method(cls, *args, **kwargs):
                return args, kwargs, uuid.uuid4()

            @lru_cache()
            def method(self, *args, **kwargs):
                return args, kwargs, uuid.uuid4()

        class ClsWithHash(object):
            def __hash__(self):
                return 0

        class ClsWithoutHash(object):
            pass

        # test func
        ret = func('func_test')
        self.assertEqual(ret, func('func_test'))
        self.assertTrue(ret != func('func_test2'))
        self.assertEqual(func(), func())

        self.assertEqual(func.lru_size(), 3)
        self.assertEqual(func.lru_hits(), 2)
        self.assertEqual(func.lru_misses(), 3)

        # test hash
        func.lru_clear_all()
        ret = func(ClsWithHash())
        self.assertEqual(ret, func(ClsWithHash()))

        self.assertEqual(func.lru_size(), 1)
        self.assertEqual(func.lru_hits(), 1)
        self.assertEqual(func.lru_misses(), 1)

        # test list
        func.lru_clear_all()
        ret = func([1, 2, 3], test=[])
        self.assertEqual(ret, func([1, 2, 3], test=[]))
        func([1, 2, 3], test=["test"])
        func([1, 2], test=["test"])

        self.assertEqual(func.lru_size(), 3)
        self.assertEqual(func.lru_hits(), 1)
        self.assertEqual(func.lru_misses(), 3)

        # test set
        func.lru_clear_all()
        ret = func(set([1, 2, 3]), test=set([]))
        self.assertEqual(ret, func(set([1, 2, 3]), test=set([])))
        func(set([1, 2, 3]), test=set(["test"]))
        func(set([1, 2]), test=set(["test"]))

        self.assertEqual(func.lru_size(), 3)
        self.assertEqual(func.lru_hits(), 1)
        self.assertEqual(func.lru_misses(), 3)

        # test cls method
        ret = Cls.cls_method('cls_method_test')
        self.assertEqual(ret, Cls.cls_method('cls_method_test'))
        self.assertTrue(ret != Cls.cls_method('cls_method_test2'))
        self.assertEqual(Cls.cls_method(), Cls.cls_method())

        # test method
        cls = Cls()
        ret = cls.method('method_test')
        self.assertTrue(Cls.cls_method('method_test') != cls.method('method_test'))
        self.assertEqual(ret, cls.method('method_test'))
        self.assertTrue(ret != cls.method('method_test2'))
        self.assertEqual(cls.method(), cls.method())

        # test clear
        self.assertEqual(ret, cls.method('method_test'))
        cls.method.lru_clear_all()
        self.assertTrue(ret != cls.method('method_test'))
        ret = cls.method('method_test')
        self.assertEqual(ret, cls.method('method_test'))
        cls.method.lru_clear(args=[cls, 'method_test'])
        self.assertTrue(ret != cls.method('method_test'))

        # test set
        func.lru_set("123")
        self.assertEqual("123", func())

        cls.method.lru_set("123", args=[cls, 'method_set_test'])
        self.assertEqual("123", cls.method('method_set_test'))

        cls.method.lru_set("456", args=[cls])
        self.assertEqual("456", cls.method())

        Cls.cls_method.lru_set("123", args=[Cls, 'cls_method_set_test'])
        self.assertEqual("123", Cls.cls_method('cls_method_set_test'))

        # test clear all
        lru_clear_all()
        self.assertTrue("123" != Cls.cls_method('cls_method_set_test'))

    def test_lru_max_size(self):
        @lru_cache(1)
        def func(*args, **kwargs):
            return args, kwargs, uuid.uuid4()

        func('func_test')
        func('func_test')
        func('func_test2')
        func('func_test3')
        func.lru_set("123", args=['func_test4'])

        self.assertEqual(func.lru_size(), 1)
        self.assertEqual(func.lru_hits(), 1)
        self.assertEqual(func.lru_misses(), 3)

    def test_lru_expires(self):
        @lru_cache(expires=1)
        def func(*args, **kwargs):
            return args, kwargs, uuid.uuid4()

        func('func_test')

        time.sleep(2)

        func('func_test')

        self.assertEqual(func.lru_size(), 1)
        self.assertEqual(func.lru_hits(), 0)
        self.assertEqual(func.lru_misses(), 2)

    def test_mem(self):
        @mem_cache()
        def func(*args, **kwargs):
            return args, kwargs, uuid.uuid4()

        class ClsWithRepr(object):
            @classmethod
            @mem_cache()
            def cls_method(cls, *args, **kwargs):
                return args, kwargs, uuid.uuid4()

            @mem_cache()
            def method(self, *args, **kwargs):
                return args, kwargs, uuid.uuid4()

            def __repr__(self):
                return "Cls <MyUniqueInstance>"

        class ClsWithoutRepr(object):
            @mem_cache()
            def method(self, *args, **kwargs):
                return args, kwargs, uuid.uuid4()

        # test func
        ret = func('func_test')
        self.assertEqual(ret, func('func_test'))
        self.assertTrue(ret != func('func_test2'))
        self.assertEqual(func(), func())

        self.assertEqual(func.mem_hits(), 2)
        self.assertEqual(func.mem_misses(), 3)

        # test cls method
        ret = ClsWithRepr.cls_method('cls_method_test')
        self.assertEqual(ret, ClsWithRepr.cls_method('cls_method_test'))
        self.assertTrue(ret != ClsWithRepr.cls_method('cls_method_test2'))
        self.assertEqual(ClsWithRepr.cls_method(), ClsWithRepr.cls_method())

        # test method
        cls = ClsWithRepr()
        ret = cls.method('method_test')
        self.assertTrue(ClsWithRepr.cls_method('method_test') != cls.method('method_test'))
        self.assertEqual(ret, cls.method('method_test'))
        self.assertTrue(ret != cls.method('method_test2'))
        self.assertEqual(cls.method(), cls.method())

        # test set
        cls.method.mem_set("123", args=(cls, 'method_set_test'))
        self.assertEqual("123", cls.method('method_set_test'))

        ClsWithRepr.cls_method.mem_set("123", args=(ClsWithRepr, 'cls_method_set_test'))
        self.assertEqual("123", ClsWithRepr.cls_method('cls_method_set_test'))

        # test exception
        cls = ClsWithoutRepr()
        self.assertRaises(Exception, cls.method)
