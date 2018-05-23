# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
import os
from os.path import join

from calmjs.toolchain import Spec
from calmjs.sassy import toolchain

from calmjs.testing.utils import mkdtemp


class BaseToolchainTestCase(unittest.TestCase):

    def test_assemble_minimum_information(self):
        working_dir = mkdtemp(self)
        os.mkdir(join(working_dir, 'package'))
        demo_scss = join(working_dir, 'package', 'demo.scss')

        with open(demo_scss, 'w') as fd:
            fd.write('body { color: #000; }')

        libsass = toolchain.BaseScssToolchain()
        spec = Spec(
            transpile_sourcepath={'demo': demo_scss},
            bundle_sourcepath={},
            build_dir=mkdtemp(self),
            calmjs_sassy_entry_points=['package/demo'],
        )
        libsass.prepare(spec)
        libsass.compile(spec)
        libsass.assemble(spec)

        assemble_path = join(
            spec['build_dir'], '__calmjs_sassy__', 'calmjs.sassy.scss')

        with open(assemble_path) as fd:
            self.assertEqual('@import "package/demo";\n', fd.read())

    def test_assemble_with_entry_point_name_not_overwriting(self):
        # normally an source index.scss being available on the build
        # dir is unlikely to happen, but this case should be properly
        # accounted for, which is why a dedicated assemble subdirectory
        # is provided.
        working_dir = mkdtemp(self)
        index_scss = join(working_dir, 'index.scss')

        with open(index_scss, 'w') as fd:
            fd.write('body { color: #000; }')

        libsass = toolchain.BaseScssToolchain()
        spec = Spec(
            transpile_sourcepath={},
            bundle_sourcepath={'index': index_scss},
            build_dir=mkdtemp(self),
            calmjs_sassy_entry_points=['index'],
            calmjs_sassy_entry_point_name='index',
        )
        libsass.prepare(spec)
        libsass.compile(spec)
        libsass.assemble(spec)

        assemble_path = join(
            spec['build_dir'], '__calmjs_sassy__', 'index.scss')

        with open(assemble_path) as fd:
            self.assertEqual('@import "index";\n', fd.read())

        with open(join(spec['build_dir'], 'index.scss')) as fd:
            self.assertEqual('body { color: #000; }', fd.read())
