# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest

from calmjs.toolchain import Spec
from calmjs.sassy import exc
from calmjs.sassy import toolchain

from calmjs.testing.utils import mkdtemp
from calmjs.testing.utils import stub_item_attr_value


class BaseToolchainTestCase(unittest.TestCase):

    def test_missing_libsass(self):
        stub_item_attr_value(self, toolchain, 'HAS_LIBSASS', False)
        with self.assertRaises(exc.CalmjsSassyRuntimeError):
            libsass = toolchain.LibsassToolchain()
            spec = Spec(
                transpile_sourcepath={},
                bundle_sourcepath={},
                build_dir=mkdtemp(self),
            )
            libsass(spec)
