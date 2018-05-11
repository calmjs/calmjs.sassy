# -*- coding: utf-8 -*-
import unittest
import os
from os.path import join

from calmjs.toolchain import Spec
from calmjs.sassy.cli import create_spec
from calmjs.utils import pretty_logging

from calmjs.testing.mocks import StringIO
from calmjs.testing.utils import mkdtemp
from calmjs.testing.utils import remember_cwd


class SpecTestCase(unittest.TestCase):
    """
    Test the spec generation.

    Most of the tests will be done in the toolchain and/or integration
    tests.
    """

    def setUp(self):
        remember_cwd(self)
        self.cwd = mkdtemp(self)
        os.chdir(self.cwd)

    def test_create_spec_integration(self):
        with pretty_logging(stream=StringIO()) as stream:
            spec = create_spec(['calmjs.sassy'])
        self.assertIn('automatically picked registries', stream.getvalue())
        self.assertTrue(isinstance(spec, Spec))
        self.assertEqual(
            join(self.cwd, 'calmjs.sassy.css'), spec['export_target'])

    def test_create_spec_blank(self):
        with pretty_logging(stream=StringIO()) as stream:
            spec = create_spec([])
        self.assertIn(
            'no packages and registries specified for spec construction',
            stream.getvalue())
        self.assertTrue(isinstance(spec, Spec))
        self.assertEqual(
            join(self.cwd, 'calmjs.sassy.export.css'), spec['export_target'])
