# This file is part of Checkbox.
#
# Copyright 2013 Canonical Ltd.
# Written by:
#   Zygmunt Krynicki <zygmunt.krynicki@canonical.com>
#
# Checkbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Checkbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Checkbox.  If not, see <http://www.gnu.org/licenses/>.

"""
checkbox.test_resource
======================

Test definitions for :mod:`checkbox.resource`
"""

from unittest import TestCase

from checkbox.resource import ResourceIterator
from checkbox.resource import ResourceMap


class ResourceMapTests(TestCase):

    def setUp(self):
        # Create a resource map with two resources:
        #
        # 'resource_list' is a list with two values, each with an 'attr'
        # attribute. This is how resources with multiple values are normally
        # stored.
        #
        # 'resource_tuple' is similar to 'resource_list', holding the same data
        # but using a tuple instead of a list.
        #
        # 'resource_dict' is a dictionary with one attribute 'name'. This is
        # how resources with one value might be stored.
        self.resource_map = ResourceMap({
            'resource_list': [
                {"attr": "value"},
                {"attr": "other-value"}
            ],
            'resource_tuple': (
                {"attr": "value"},
                {"attr": "other-value"}
            ),
            'resource_dict': {"attr": "value"},
            'resource_int': 42,
        })
        # This is an empty map, it is used by some of the tests
        self.empty_map = ResourceMap()

    def test_resource_map_is_a_dict(self):
        # While it's a derived class it's still a dictionary
        self.assertIsInstance(self.resource_map, dict)

    def test_missing_resource(self):
        # Missing resources just raise KeyError as they normally would in a
        # dictionary
        with self.assertRaises(KeyError):
            self.resource_map['resource_missing']

    def test_existing_resource_list(self):
        # Accessing a resource wrapped in a list returns a ResourceIterator
        thing = self.resource_map['resource_list']
        self.assertIsInstance(thing, ResourceIterator)

    def test_existing_resource_tuple(self):
        # Accessing a resource wrapped in a tuple returns a ResourceIterator
        thing = self.resource_map['resource_tuple']
        self.assertIsInstance(thing, ResourceIterator)

    def test_existing_resource_dict(self):
        # Accessing a resource wrapped in a dict returns a ResourceIterator
        thing = self.resource_map['resource_dict']
        self.assertIsInstance(thing, ResourceIterator)

    def test_existing_resource_int(self):
        # Accessing a resource wrapped in a int returns the value directly
        thing = self.resource_map['resource_int']
        self.assertIsInstance(thing, int)
        # The helper integer is 42
        self.assertEqual(thing, 42)

    def test_eval_smoke(self):
        # Evaluating anything valid against an empty map returns None
        self.assertIs(None, self.empty_map.eval("resource.attr == 'value'"))
        # Evaluating borked code against an empty map also returns None
        self.assertIs(None, self.empty_map.eval("adpasdasd .asdaasd asd a"))

    def test_under_results(self):
        # The resource map has an instance variable, _results that is only
        # assigned after the call to ResourceMap.eval().
        with self.assertRaises(AttributeError):
            self.empty_map._results
        # Calling eval() initializes/overrides it
        self.empty_map.eval('')
        # With an empty list (that list may contain other values normally but
        # with an empty resource map it is always empty)
        self.assertEqual(self.empty_map._results, [])

    def test_eval_globals(self):
        # ResourceMap.eval() has a fixed list of globals
        #
        # We can poke at that list by using specially crafted expressions.
        # Each time the expression evaluates to 1, we get an empty list back.
        self.assertEqual([], self.empty_map.eval("'bool' in globals() and 1"))
        self.assertEqual([], self.empty_map.eval("'float' in globals() and 1"))
        self.assertEqual([], self.empty_map.eval("'int' in globals() and 1"))
        self.assertEqual([], self.empty_map.eval("'str' in globals() and 1"))
        # Each of those globals is a special ResourceBuiltin object
        self.assertEqual([], self.resource_map.eval(
            "bool.__class__.__name__ == 'ResourceBuiltin'"))
        self.assertEqual([], self.resource_map.eval(
            "float.__class__.__name__ == 'ResourceBuiltin'"))
        self.assertEqual([], self.resource_map.eval(
            "int.__class__.__name__ == 'ResourceBuiltin'"))
        self.assertEqual([], self.resource_map.eval(
            "str.__class__.__name__ == 'ResourceBuiltin'"))
        # Unfortunately, __builtins__ is also in the global scope
        #
        # With builtins being available we have a way to access anything in
        # python via __import__
        self.assertEqual([], self.empty_map.eval(
            "'__builtins__' in globals() and 1"))
        # There are no other globals than what was checked for above:
        #
        # The goal is to ensure that there are only particular globals
        # in the context that is being used to evaluate the expression.
        #
        # We cannot return the value directly and compare it outside
        # (well we can but that trick is used later to keep this code
        # simple and portable across changes in checkbox)
        #
        # The return value of globals().keys() is a special dict_keys() proxy
        # that returns the items in undetermined order.
        #
        # The result is a simple comparison of two sorted list generated by
        # list comprehensions from iterating over all the keys in global() and
        # in the list of expected global symbols
        self.assertEqual([], self.empty_map.eval(
            "sorted([x for x in globals().keys()])"
            " == "
            "sorted(['__builtins__', 'bool', 'float', 'int', 'str'])"))

    def test_eval_locals(self):
        # As with the globals test above, this test checks what kind of locals
        # are available inside the execution context.
        #
        # In the example of an empty map, the result is -- no locals!
        self.assertEqual([], self.empty_map.eval(
            "sorted([x for x in locals().keys()])"
            " == "
            "[]"))
        # In the example of a resource map with several resources the result
        # are those resources (after wrapping in ResourceIterator)
        self.assertEqual([], self.resource_map.eval(
            "sorted([x for x in locals().keys()])"
            " == "
            "sorted(['resource_list', 'resource_tuple',"
            "        'resource_dict', 'resource_int'])"))
        # Let's just ensure that those are not the raw values anymore Note that
        # we cannot use 'int', 'list', etc. directly they are wrapped in
        # ResourceBuiltin objects (see test_eval_globals() above)
        self.assertEqual([], self.resource_map.eval(
            "locals()['resource_int'] != (0).__class__"))
        self.assertEqual([], self.resource_map.eval(
            "locals()['resource_dict'] != ({}).__class__"))
        self.assertEqual([], self.resource_map.eval(
            "locals()['resource_list'] != ([]).__class__"))
        self.assertEqual([], self.resource_map.eval(
            "locals()['resource_tuple'] != (()).__class__"))

    def test_eval_import(self):
        # The expression can import arbitrary python package
        #
        # Here we import the subprocess module, execute /bin/false which
        # returns 1, this makes the expression True in the terms of checkbox
        # resource programs.
        self.assertEqual([], self.empty_map.eval(
            "__import__('subprocess').call('/bin/false')"))

    def test_eval_can_mutate_results(self):
        # The ResourceMap._results object can be accessed and mutated
        # by using locals(). Calling locals() inside the expression literally
        # returns the ResourceMap instance.
        #
        # Using that trick, any operation can be performed, including mutating
        # or replacing the results object.
        results = self.empty_map.eval(
            "1 "
            "if getattr(locals(), '_results').append('payload') "
            "is None "
            "else 0")
        self.assertIs(self.empty_map._results, results)
        self.assertEqual(results, ['payload'])

    def test_eval_return_value_for_int_resources(self):
        # This test explores how resource_map.eval() result gets
        # computed and what it really is in practice.
        #
        # The important aspect of this code is that it relies on
        # ResourceMap._results being shared by ResourceMap, ResourceIterator
        # and ResourceObject. This makes testing the behavior in isolation
        # difficult.
        #
        # Technically _results are mutated only in ResourceIterator (in the
        # __contains__ function) and in the ResourceObject (in the _try
        # function that is in turn called from all overridden special functions
        # like __eq__) both of those places call _results.append().
        #
        # The appended value is either the element of the ResourceIterator
        # (technically the value) and the converted value of the attribute in
        # ResourceObject._try. This is rather confusing so let's see what
        # happens in practice.
        #
        # Let's explore resource_list first (the flow is the same for all other
        # types so the explanations are only given once).
        #
        # Here each value was a simple dictionary with 'attr' key wrapped in a
        # list. As checked earlier by test_existing_resource_list() that list
        # is converted to a ResourceIterator. Accessing any attribute on the
        # resource iterator creates a ResourceObject bound to that attribute
        # name and the iterator. Calling the equality operator on a
        # ResourceObject calls ResourceObject.__eq__() which in turns calls
        # ResourceObject._try() The _try() function iterates over the
        # ResourceIterator and checks of any of the items returned (which are
        # the raw items as passed to ResourceMap initially) have an entry
        # corresponding to the attribute name (that was accessed on
        # ResourceIterator), if so, the value is looked up, converted using the
        # convert function (identity by default), and passed to the helper
        # function (that corresponds to the logical operation performed by
        # whatever called _try, for example, __eq__ calls lambda a, b: a == b).
        # If the return value of that function matches the expected sentinel
        # object (True is used by default) then the loop over the iterator
        # (inside _try()) is broken and the original item (the dictionary or
        # other object that was initially passed to the ResourceMap) is
        # appended. Lastly the _try() method returns the sentinel object (True
        # by default) there was a match (the loop got broken) or the default
        # value (False by default) otherwise. This is all pretty complicated
        # but in the case of all-defaults it's pretty much equivalent to:
        #
        # results = [
        #     object
        #     for object in resource_map[resource_name]
        #     if object.get(resource_attr) == expected_value]
        #
        # Let's see how that works in practice.
        # Note that the == operator can be replaced by any operator
        # supported by ResourceObject (<, <=, >, >=, =, !=, in)
        self.assertEqual(
            self.resource_map.eval("resource_list.attr == 'value'"),
            [{'attr': 'value'}])
        self.assertEqual(
            self.resource_map.eval("resource_list.attr in ['value']"),
            [{'attr': 'value'}])
        self.assertEqual(
            self.resource_map.eval("resource_list.attr != 'value'"),
            [{'attr': 'other-value'}])
        # The inequality operator used with a value that does not exist in the
        # resource produces the full list of resources back.
        self.assertEqual(
            self.resource_map.eval("resource_list.attr != 'foo'"),
            [{'attr': 'value'}, {'attr': 'other-value'}])

    def test_eval_return_value_for_tuple_resources(self):
        # Set of identical tests for resource_tuple
        self.assertEqual(
            self.resource_map.eval("resource_tuple.attr == 'value'"),
            [{'attr': 'value'}])
        self.assertEqual(
            self.resource_map.eval("resource_tuple.attr in ['value']"),
            [{'attr': 'value'}])
        self.assertEqual(
            self.resource_map.eval("resource_tuple.attr != 'value'"),
            [{'attr': 'other-value'}])

    def test_eval_return_value_for_dict_resources(self):
        # Set of identical tests for resource_dict
        self.assertEqual(
            self.resource_map.eval("resource_dict.attr == 'value'"),
            [{'attr': 'value'}])
        self.assertEqual(
            self.resource_map.eval("resource_dict.attr in ['value']"),
            [{'attr': 'value'}])
        # Here the result is slightly different. This is because there are no
        # matches (there is no 'other-value' like in previous cases). In such
        # case the whole expression does not evaluate to True and the return
        # value is None.
        self.assertEqual(
            self.resource_map.eval("resource_dict.attr != 'value'"),
            None)

    def test_eval_return_value_for_other_resources(self):
        # Set of identical tests for resource_int
        #
        # Here resource_int is not wrapped in a ResourceIterator and unexpected
        # things start to happen. There is no logic to modify the result in
        # such case so although the result of the comparison is True the result
        # of the eval() function is the empty results list.
        #
        # I suspect that such cases were never meant to happen and are an
        # oversight from the initial implementation and lack of testing beyond
        # the expected working cases.
        self.assertEqual(
            self.resource_map.eval("resource_int == 42"),
            [])
        # Confusingly enough, but consistently, when the expression evaluates
        # the False the eval() function returns None.
        self.assertEqual(
            self.resource_map.eval("resource_int != 42"),
            None)

    def test_eval_return_logic_bool(self):
        # There is some extra logic in eval() that should be documented.
        # The return value of the low-level eval() call inside the
        # ResourceMap.eval() method is passed to a set of tests to determine if
        # it is 'true enough' to return the results. Those tests include:
        # 1) A boolean value which is True
        self.assertEqual([], self.empty_map.eval("True"))
        self.assertEqual(None, self.empty_map.eval("False"))

    def test_eval_return_logic_int(self):
        # 2) A non-zero integer
        self.assertEqual([], self.empty_map.eval("1"))
        self.assertEqual(None, self.empty_map.eval("0"))

    def test_eval_return_logic_tuple(self):
        # 3) A tuple with at least one True object
        self.assertEqual([], self.empty_map.eval("(True,)"))
        self.assertEqual([], self.empty_map.eval("(False, True, 7)"))
        self.assertEqual(None, self.empty_map.eval("(False, 7)"))
        self.assertEqual(None, self.empty_map.eval("(7,)"))
        self.assertEqual(None, self.empty_map.eval("()"))

    def test_eval_return_logic_list(self):
        # Sadly this does not apply to lists
        self.assertEqual(None, self.empty_map.eval("[True]"))
