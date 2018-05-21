# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest

from calmjs.utils import pretty_logging
from calmjs.toolchain import Spec
from calmjs.sassy import exc
from calmjs.sassy import toolchain

from calmjs.testing.mocks import StringIO
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


class StubImporterTestCase(unittest.TestCase):

    def test_resolve_well_defined(self):
        # for a thing that is fully defined.
        spec = {
            'export_module_names': [
                'example/slim/index',
                'example/slim/common',
            ],
            'calmjs_sassy_sourcepath_merged': {
                'fakestrap': '/node_modules/fakestrap',
                'example/slim/common': '/src/example/slim/common.scss',
                'example/slim/index': '/src/example/slim/index.scss',
                'example/usage/colors': '/src/example/package/colors.scss',
                'example/usage/extras': '/src/example/usage/extras.scss',
                'example/usage/index': '/src/example/usage/index.scss',
            },
            'transpile_sourcepath': {
                'example/slim/index': '/somewhere/example/slim/index.scss',
                'example/slim/common': '/somewhere/example/slim/common.scss',
            },
            'transpiled_modpaths': {
                'example/slim/index': 'example/slim/index',
                'example/slim/common': 'example/slim/common',
            },
            'transpiled_targetpaths': {
                'example/slim/index': 'example/slim/index.scss',
                'example/slim/common': 'example/slim/common.scss',
            },
        }
        resolve_stub_importer = toolchain.libsass_import_stub_generator(spec)
        # it is provided
        self.assertIsNone(resolve_stub_importer('example/slim/common'))
        # defined sheet
        self.assertEqual(
            (('example/usage/colors', ''),),
            resolve_stub_importer('example/usage/colors'),
        )
        # resolving a defined subpath in a defined path
        with pretty_logging(stream=StringIO()) as stream:
            self.assertEqual(
                (('fakestrap/some/style', ''),),
                resolve_stub_importer('fakestrap/some/style'),
            )

        self.assertIn(
            "generating stub import for 'fakestrap/some/style'; "
            "provided by 'fakestrap'", stream.getvalue())
        # an undeclared stylesheet will not be handled, which will most
        # certainly trigger an import error.
        self.assertIsNone(resolve_stub_importer('undeclared/sheet'))
