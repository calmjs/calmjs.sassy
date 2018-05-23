# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
import os
import sys
from textwrap import dedent
from os.path import exists
from os.path import join

from calmjs.utils import pretty_logging
from calmjs.toolchain import Spec
from calmjs.runtime import main
from calmjs.registry import get as get_registry

from calmjs.sassy import libsass
from calmjs.sassy.cli import compile_all
from calmjs.sassy import exc

from calmjs.sassy import libsass_runtime

from calmjs.testing.mocks import StringIO
from calmjs.testing.utils import mkdtemp
from calmjs.testing.utils import remember_cwd
from calmjs.testing.utils import stub_stdouts
from calmjs.sassy.testing.utils import setup_class_integration_environment
from calmjs.sassy.testing.utils import teardown_class_integration_environment


@unittest.skipIf(
    not libsass.HAS_LIBSASS, "'libsass' package is not installed")
class ToolchainIntegrationTestCase(unittest.TestCase):
    """
    Test out the full toolchain, involving webpack completely.
    """

    # Ensure that webpack is properly installed through the calmjs
    # framework and specification for this package.  This environment
    # will be reused for the duration for this test.

    @classmethod
    def setUpClass(cls):
        setup_class_integration_environment(cls)

    @classmethod
    def tearDownClass(cls):
        teardown_class_integration_environment(cls)

    def setUp(self):
        pass

    def tearDown(self):
        # remove registries that got polluted with test data
        from calmjs.registry import _inst as root_registry
        root_registry.records.pop('calmjs.artifacts', None)

    def test_libsass_toolchain_direct_execution(self):
        """
        Execute the toolchain with a minimum constructed spec
        """

        # this is the most barebone, minimum execution with only just
        # the required spec keys.
        bundle_dir = mkdtemp(self)
        build_dir = mkdtemp(self)
        transpile_sourcepath = {
            'example/package/colors': join(self._ep_root, 'colors.scss'),
        }
        bundle_sourcepath = {}
        export_target = join(bundle_dir, 'example.package.css')
        toolchain = libsass.LibsassToolchain()
        spec = Spec(
            transpile_sourcepath=transpile_sourcepath,
            bundle_sourcepath=bundle_sourcepath,
            export_target=export_target,
            build_dir=build_dir,
            calmjs_sassy_entry_points=('example/package/colors',),
        )
        toolchain(spec)
        self.assertEqual({
            'example/package/colors': 'example/package/colors.scss',
        }, spec['transpiled_targetpaths'])
        # need to actually integrate libsass

        self.assertTrue(exists(export_target))
        with open(export_target) as fd:
            # since colors.scss does not define any styling rules.
            self.assertEqual('', fd.read())

    def test_libsass_toolchain_manual_standard_execution(self):
        """
        Execute the toolchain with a spec that might be typically
        generated.
        """

        # this is the most barebone, minimum execution with only just
        # the required spec keys.
        bundle_dir = mkdtemp(self)
        build_dir = mkdtemp(self)
        transpile_sourcepath = {
            'example/package/index': join(self._ep_root, 'index.scss'),
            'example/package/colors': join(self._ep_root, 'colors.scss'),
        }
        bundle_sourcepath = {}
        export_target = join(bundle_dir, 'example.package.css')
        toolchain = libsass.LibsassToolchain()
        spec = Spec(
            transpile_sourcepath=transpile_sourcepath,
            bundle_sourcepath=bundle_sourcepath,
            export_target=export_target,
            build_dir=build_dir,
            calmjs_sassy_entry_points=('example/package/index',),
        )
        toolchain(spec)
        self.assertEqual({
            'example/package/colors': 'example/package/colors.scss',
            'example/package/index': 'example/package/index.scss',
        }, spec['transpiled_targetpaths'])
        # need to actually integrate libsass

        self.assertTrue(exists(export_target))
        with open(export_target) as fd:
            # the definition in colors.scss will be merged in.
            self.assertEqual(
                'body {\n  background-color: #f00; }\n', fd.read())

    def test_libsass_compile_error(self):
        malformed_scss = join(self._ep_root, 'malformed.scss')
        with open(malformed_scss, 'w') as fd:
            fd.write(
                'var foo = "bar";\n'
            )

        bundle_dir = mkdtemp(self)
        build_dir = mkdtemp(self)
        transpile_sourcepath = {
            'example/package/malformed': malformed_scss,
        }
        export_target = join(bundle_dir, 'example.package.css')
        toolchain = libsass.LibsassToolchain()
        spec = Spec(
            transpile_sourcepath=transpile_sourcepath,
            bundle_sourcepath={},
            export_target=export_target,
            build_dir=build_dir,
            calmjs_sassy_entry_points=('example/package/malformed',),
        )
        with self.assertRaises(exc.CalmjsSassyRuntimeError):
            toolchain(spec)

    def test_libsass_compile_all(self):
        """
        Execute the toolchain with a spec that might be typically
        generated.
        """

        working_dir = mkdtemp(self)
        with pretty_logging(stream=StringIO()) as stream:
            spec = compile_all(['example.package'], working_dir=working_dir)
        export_target = spec['export_target']
        self.assertEqual(
            export_target, join(working_dir, 'example.package.css'))
        # check that the toolchain was invoked to "transpile" scss.
        self.assertEqual({
            'example/package/colors': 'example/package/colors.scss',
            'example/package/index': 'example/package/index.scss',
        }, spec['transpiled_targetpaths'])

        self.assertTrue(exists(export_target))
        with open(export_target) as fd:
            # the definition in colors.scss will be merged in.
            self.assertEqual(
                'body {\n  background-color: #f00; }\n', fd.read())

        self.assertIn("automatically picked registries", stream.getvalue())
        self.assertIn("'calmjs.scss'] for sourcepaths", stream.getvalue())

    def test_libsass_compile_all_explicit_entry_point(self):
        """
        Execute the toolchain with a spec that might be typically
        generated.
        """

        working_dir = mkdtemp(self)
        with pretty_logging(stream=StringIO()) as stream:
            spec = compile_all(
                ['example.usage'], working_dir=working_dir,
                calmjs_sassy_entry_point_name='extras',
            )
        export_target = spec['export_target']
        self.assertEqual(
            export_target, join(working_dir, 'example.usage.css'))
        # check that the toolchain was invoked to "transpile" scss.
        self.assertEqual({
            # everything up the dependency graph is indiscriminately
            # copied.
            'example/package/colors': 'example/package/colors.scss',
            'example/package/index': 'example/package/index.scss',
            'example/usage/extras': 'example/usage/extras.scss',
            'example/usage/index': 'example/usage/index.scss',
        }, spec['transpiled_targetpaths'])

        self.assertTrue(exists(export_target))
        with open(export_target) as fd:
            # only the standalone extras.scss file will be used, however
            self.assertEqual('h1 {\n  font-weight: bold; }\n', fd.read())

        self.assertIn("automatically picked registries", stream.getvalue())
        self.assertIn("'calmjs.scss'] for sourcepaths", stream.getvalue())

    def test_libsass_compile_all_manual(self):
        """
        Various manual options, to verify extra logging outputs.
        """

        remember_cwd(self)
        os.chdir(mkdtemp(self))

        # with manual source registry
        with pretty_logging(stream=StringIO()) as stream:
            spec = compile_all(
                ['example.package'], source_registries=['calmjs.scss'])

        self.assertTrue(exists(spec['export_target']))
        log = stream.getvalue()
        self.assertIn("using manually specified registries", log)
        self.assertIn("'calmjs.scss'] for sourcepaths", log)

        # with manual source registry
        with pretty_logging(stream=StringIO()) as stream:
            spec = compile_all(
                ['example.package'],
                calmjs_sassy_entry_points=['example/package/index'],
            )

        self.assertTrue(exists(spec['export_target']))
        log = stream.getvalue()
        self.assertIn('using provided targets ', log)
        self.assertIn("'example/package/index'] as entry points for css", log)

    def test_libsass_compile_all_compact(self):
        """
        Execute the toolchain with a spec that might be typically
        generated.
        """

        working_dir = mkdtemp(self)
        with pretty_logging(stream=StringIO()):
            spec = compile_all(
                ['example.package'], working_dir=working_dir,
                libsass_output_style='compact',
            )
        export_target = spec['export_target']
        self.assertEqual(
            export_target, join(working_dir, 'example.package.css'))
        self.assertTrue(exists(export_target))
        with open(export_target) as fd:
            self.assertEqual(
                'body { background-color: #f00; }\n', fd.read())

    def test_no_such_package(self):
        with pretty_logging(stream=StringIO()) as stream:
            with self.assertRaises(exc.CalmjsSassyRuntimeError):
                compile_all(['example.no.such.package'])

        log = stream.getvalue()
        self.assertIn("no module registry declarations found", log)
        self.assertIn("example.no.such.package", log)

    def test_dependencies(self):
        remember_cwd(self)
        os.chdir(mkdtemp(self))

        with pretty_logging(stream=StringIO()) as stream:
            spec = compile_all(['example.usage'])

        # ensure that only the relevant index is used.
        log = stream.getvalue()
        self.assertNotIn("'example/package/index'", log)
        self.assertIn("'example/usage/index'] as entry points for css", log)

        with open(spec['export_target']) as fd:
            self.assertEqual(dedent('''
            h1 {
              font-weight: bold; }

            body {
              color: #f00; }
            ''').lstrip(), fd.read())

    def test_slim_with_index_dependencies(self):
        remember_cwd(self)
        # using the dist_dir as that's where the fake_modules is located
        os.chdir(self.dist_dir)

        with pretty_logging(stream=StringIO()):
            spec = compile_all(['example.slim'])

        with open(spec['export_target']) as fd:
            self.assertEqual(dedent('''
            .mockstrap {
              color: #f00; }

            h1 {
              font-weight: bold; }

            body {
              font-weight: lighter; }
            ''').lstrip(), fd.read())

    def test_slim_explicit_sourcepath(self):
        remember_cwd(self)
        os.chdir(self.dist_dir)

        with pretty_logging(stream=StringIO()):
            spec = compile_all(['example.slim'], sourcepath_method='explicit')

        with open(spec['export_target']) as fd:
            # the main section is not included
            self.assertEqual(dedent('''
            .mockstrap {
              color: #f00; }

            body {
              font-weight: lighter; }
            ''').lstrip(), fd.read())

    def test_slim_no_bundlepath(self):
        remember_cwd(self)
        os.chdir(self.dist_dir)

        with pretty_logging(stream=StringIO()):
            spec = compile_all(['example.slim'], bundlepath_method='none')

        with open(spec['export_target']) as fd:
            # the main section is not included
            self.assertEqual(dedent('''
            h1 {
              font-weight: bold; }

            body {
              font-weight: lighter; }
            ''').lstrip(), fd.read())

    def test_usage_all_explicit_fail(self):
        remember_cwd(self)
        os.chdir(self.dist_dir)
        with pretty_logging(stream=StringIO()):
            with self.assertRaises(exc.CalmjsSassyRuntimeError):
                compile_all(
                    ['example.usage'], sourcepath_method='explicit',
                    bundlepath_method='none',
                )

    def test_runtime_integration_successful(self):
        """
        Test the runtime integration.
        """

        stub_stdouts(self)
        working_dir = mkdtemp(self)
        spec = libsass_runtime([
            'example.package', '-vv', '--working-dir', working_dir,
        ])
        log = sys.stderr.getvalue().replace("u'", "'")
        self.assertIn(
            "DEBUG calmjs.sassy.toolchain wrote entry point module that will "
            "import from the following: ['example/package/index']",
            log)
        self.assertIn("wrote export css file at", log)
        with open(spec['export_target']) as fd:
            self.assertEqual(
                'body {\n  background-color: #f00; }\n', fd.read())

    def test_runtime_compressed_output(self):
        """
        Test the runtime integration.
        """

        stub_stdouts(self)
        working_dir = mkdtemp(self)
        spec = libsass_runtime([
            'example.package', '-vv',
            '--working-dir', working_dir,
            '--style', 'compressed',
        ])
        log = sys.stderr.getvalue().replace("u'", "'")
        self.assertIn(
            "DEBUG calmjs.sassy.toolchain wrote entry point module that will "
            "import from the following: ['example/package/index']",
            log)
        self.assertIn("wrote export css file at", log)
        with open(spec['export_target']) as fd:
            self.assertEqual(
                'body{background-color:red}\n', fd.read())

    def test_runtime_integration_failure(self):
        stub_stdouts(self)
        working_dir = mkdtemp(self)
        # Test that explicit is not going to work because it has a hard
        # dependency
        libsass_runtime([
            'example.usage', '-vvd', '--working-dir', working_dir,
            '--sourcepath-method=explicit',
        ])
        log = sys.stderr.getvalue().replace("u'", "'")
        self.assertIn("CRITICAL", log)
        self.assertIn('Undefined variable: "$theme-color".', log)

    def test_runtime_explicit_entry_point_name(self):
        stub_stdouts(self)
        working_dir = mkdtemp(self)
        spec = libsass_runtime([
            'artifact', 'build', 'example.usage',
            '--working-dir', working_dir,
            '--entry-point-name=extras',
        ])
        with open(spec['export_target']) as fd:
            self.assertEqual('h1 {\n  font-weight: bold; }\n', fd.read())

    def test_artifact_runtime_entry_point_integration(self):
        # Note that this test causes irreversable side effects for the
        # remainder of the test, as the egg-info artifact written is
        # not cleaned up at the end as the artifacts are generated
        # directly onto the class level test environment.
        stub_stdouts(self)
        registry = get_registry('calmjs.artifacts')
        builders = sorted(
            registry.iter_builders_for('example.usage'),
            key=lambda builder: str(builder[0])
        )
        for e, t, spec in builders:
            self.assertFalse(exists(spec['export_target']))

        self.assertEqual(2, len(builders))
        with self.assertRaises(SystemExit) as e:
            main(['artifact', 'build', 'example.usage'])

        self.assertEqual(e.exception.args[0], 0)
        for e, t, spec in builders:
            self.assertTrue(exists(spec['export_target']))

        with open(builders[0][2]['export_target']) as fd:
            # style.css
            self.assertEqual('h1 {\n', fd.readline())

        with open(builders[1][2]['export_target']) as fd:
            # style.min.css
            self.assertEqual(
                'h1{font-weight:bold}body{color:red}\n', fd.readline())
