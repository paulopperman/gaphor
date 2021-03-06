""" Tests for :module:`gaphor.misc.generic.multidispatch`."""

import unittest

from gaphor.misc.generic.multidispatch import multidispatch

__all__ = ("DispatcherTests",)


class DispatcherTests(unittest.TestCase):
    def createDispatcher(
        self, params_arity, args=None, varargs=None, keywords=None, defaults=None
    ):
        from inspect import ArgSpec
        from gaphor.misc.generic.multidispatch import FunctionDispatcher

        return FunctionDispatcher(
            ArgSpec(args=args, varargs=varargs, keywords=keywords, defaults=defaults),
            params_arity,
        )

    def test_one_argument(self):
        dispatcher = self.createDispatcher(1, args=["x"])

        dispatcher.register_rule(lambda x: x + 1, int)
        self.assertEqual(dispatcher(1), 2)
        self.assertRaises(TypeError, dispatcher, "s")

        dispatcher.register_rule(lambda x: x + "1", str)
        self.assertEqual(dispatcher(1), 2)
        self.assertEqual(dispatcher("1"), "11")
        self.assertRaises(TypeError, dispatcher, tuple())

    def test_two_arguments(self):
        dispatcher = self.createDispatcher(2, args=["x", "y"])

        dispatcher.register_rule(lambda x, y: x + y + 1, int, int)
        self.assertEqual(dispatcher(1, 2), 4)
        self.assertRaises(TypeError, dispatcher, "s", "ss")
        self.assertRaises(TypeError, dispatcher, 1, "ss")
        self.assertRaises(TypeError, dispatcher, "s", 2)

        dispatcher.register_rule(lambda x, y: x + y + "1", str, str)
        self.assertEqual(dispatcher(1, 2), 4)
        self.assertEqual(dispatcher("1", "2"), "121")
        self.assertRaises(TypeError, dispatcher, "1", 1)
        self.assertRaises(TypeError, dispatcher, 1, "1")

        dispatcher.register_rule(lambda x, y: str(x) + y + "1", int, str)
        self.assertEqual(dispatcher(1, 2), 4)
        self.assertEqual(dispatcher("1", "2"), "121")
        self.assertEqual(dispatcher(1, "2"), "121")
        self.assertRaises(TypeError, dispatcher, "1", 1)

    def test_bottom_rule(self):
        dispatcher = self.createDispatcher(1, args=["x"])

        dispatcher.register_rule(lambda x: x, object)
        self.assertEqual(dispatcher(1), 1)
        self.assertEqual(dispatcher("1"), "1")
        self.assertEqual(dispatcher([1]), [1])
        self.assertEqual(dispatcher((1,)), (1,))

    def test_subtype_evaluation(self):
        class Super:
            pass

        class Sub(Super):
            pass

        dispatcher = self.createDispatcher(1, args=["x"])

        dispatcher.register_rule(lambda x: x, Super)
        o_super = Super()
        self.assertEqual(dispatcher(o_super), o_super)
        o_sub = Sub()
        self.assertEqual(dispatcher(o_sub), o_sub)
        self.assertRaises(TypeError, dispatcher, object())

        dispatcher.register_rule(lambda x: (x, x), Sub)
        o_super = Super()
        self.assertEqual(dispatcher(o_super), o_super)
        o_sub = Sub()
        self.assertEqual(dispatcher(o_sub), (o_sub, o_sub))

    def test_register_rule_with_wrong_arity(self):
        dispatcher = self.createDispatcher(1, args=["x"])
        dispatcher.register_rule(lambda x: x, int)
        self.assertRaises(TypeError, dispatcher.register_rule, lambda x, y: x, str)

    def test_register_rule_with_different_arg_names(self):
        dispatcher = self.createDispatcher(1, args=["x"])
        dispatcher.register_rule(lambda y: y, int)
        self.assertEqual(dispatcher(1), 1)

    def test_dispatching_with_varargs(self):
        dispatcher = self.createDispatcher(1, args=["x"], varargs="va")
        dispatcher.register_rule(lambda x, *va: x, int)
        self.assertEqual(dispatcher(1), 1)
        self.assertRaises(TypeError, dispatcher, "1", 2, 3)

    def test_dispatching_with_varkw(self):
        dispatcher = self.createDispatcher(1, args=["x"], keywords="vk")
        dispatcher.register_rule(lambda x, **vk: x, int)
        self.assertEqual(dispatcher(1), 1)
        self.assertRaises(TypeError, dispatcher, "1", a=1, b=2)

    def test_dispatching_with_kw(self):
        dispatcher = self.createDispatcher(1, args=["x", "y"], defaults=["vk"])
        dispatcher.register_rule(lambda x, y=1: x, int)
        self.assertEqual(dispatcher(1), 1)
        self.assertRaises(TypeError, dispatcher, "1", k=1)

    def test_create_dispatcher_with_pos_args_less_multi_arity(self):
        self.assertRaises(TypeError, self.createDispatcher, 2, args=["x"])
        self.assertRaises(
            TypeError, self.createDispatcher, 2, args=["x", "y"], defaults=["x"]
        )

    def test_register_rule_with_wrong_number_types_parameters(self):
        dispatcher = self.createDispatcher(1, args=["x", "y"])
        self.assertRaises(TypeError, dispatcher.register_rule, lambda x, y: x, int, str)

    def test_register_rule_with_partial_dispatching(self):
        dispatcher = self.createDispatcher(1, args=["x", "y"])
        dispatcher.register_rule(lambda x, y: x, int)
        self.assertEqual(dispatcher(1, 2), 1)
        self.assertEqual(dispatcher(1, "2"), 1)
        self.assertRaises(TypeError, dispatcher, "2", 1)
        dispatcher.register_rule(lambda x, y: x, str)
        self.assertEqual(dispatcher(1, 2), 1)
        self.assertEqual(dispatcher(1, "2"), 1)
        self.assertEqual(dispatcher("1", "2"), "1")
        self.assertEqual(dispatcher("1", 2), "1")


class MultifunctionTests(unittest.TestCase):
    def test_default_dispatcher(self):
        @multidispatch(int, str)
        def func(x, y):
            return str(x) + y

        self.assertEqual(func(1, "2"), "12")
        self.assertRaises(TypeError, func, 1, 2)
        self.assertRaises(TypeError, func, "1", 2)
        self.assertRaises(TypeError, func, "1", "2")

    def test_multiple_functions(self):
        @multidispatch(int, str)
        def func(x, y):
            return str(x) + y

        @func.register(str, str)
        def _(x, y):
            return x + y

        self.assertEqual(func(1, "2"), "12")
        self.assertEqual(func("1", "2"), "12")
        self.assertRaises(TypeError, func, 1, 2)
        self.assertRaises(TypeError, func, "1", 2)

    def test_default(self):
        @multidispatch()
        def func(x, y):
            return x + y

        @func.register(str, str)
        def _(x, y):
            return y + x

        self.assertEqual(func(1, 1), 2)
        self.assertEqual(func("1", "2"), "21")

    def test_on_classes(self):
        @multidispatch()
        class A:
            def __init__(self, a, b):
                self.v = a + b

        @A.register(str, str)
        class B:
            def __init__(self, a, b):
                self.v = b + a

        assert A(1, 1).v == 2
        assert A("1", "2").v == "21"
