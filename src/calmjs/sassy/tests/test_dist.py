# -*- coding: utf-8 -*-
import unittest

from calmjs.sassy.dist import get_calmjs_scss_module_registry_for


class ModuleRegistryTestCase(unittest.TestCase):
    """
    Test the dist module for the selection helpers.
    """

    def test_registry_integration(self):
        registries = get_calmjs_scss_module_registry_for(['calmjs.sassy'])
        self.assertEqual(['calmjs.scss'], registries)
