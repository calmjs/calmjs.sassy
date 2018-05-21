# -*- coding: utf-8 -*-
import unittest

from calmjs.toolchain import Spec
from calmjs.toolchain import NullToolchain
from calmjs.sassy.runtime import ScssRuntime

from calmjs.testing.utils import stub_stdouts


class RuntimeTestCase(unittest.TestCase):
    """
    Basic tests for the runtime module.
    """

    def test_create_spec_integration(self):
        runtime = ScssRuntime(NullToolchain())
        stub_stdouts(self)
        spec = runtime(['calmjs.scss', '--source-registries=demo'])
        self.assertTrue(isinstance(spec, Spec))
        self.assertEqual(['demo'], spec['calmjs_module_registry_names'])
