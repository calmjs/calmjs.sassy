# -*- coding: utf-8 -*-
import unittest
from pkg_resources import EntryPoint

from calmjs.sassy.registry import SCSSRegistry
from calmjs.utils import pretty_logging

from calmjs.testing import mocks


class SCSSRegistryTestCase(unittest.TestCase):
    """
    Test the SCSSRegistry
    """

    def setUp(self):
        self.registry = SCSSRegistry(__name__)

    def test_module_registry_standard(self):
        with pretty_logging(stream=mocks.StringIO()):
            self.registry.register_entry_points([EntryPoint.parse(
                'calmjs.sassy.testing = calmjs.sassy.testing')])
        self.assertEqual(sorted(
            key for key, value in self.registry.iter_records()
        ), [
            'calmjs.sassy.testing',
        ])

        records = self.registry.get_record('calmjs.sassy.testing')
        key = 'calmjs/sassy/testing/index'
        self.assertEqual(sorted(records.keys()), [key])
