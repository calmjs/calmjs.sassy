# -*- coding: utf-8 -*-
import unittest
from pkg_resources import WorkingSet

from calmjs.sassy.registry import SCSSRegistry
from calmjs.sassy.dist import get_calmjs_scss_module_registry_for
from calmjs.sassy.dist import generate_scss_sourcepaths

from calmjs.testing.utils import make_dummy_dist
from calmjs.testing.utils import stub_item_attr_value


class ModuleRegistryTestCase(unittest.TestCase):
    """
    Test the dist module for the selection helpers.
    """

    def test_registry_integration(self):
        registries = get_calmjs_scss_module_registry_for(['calmjs.sassy'])
        self.assertEqual(['calmjs.scss'], registries)


class SourcepathTestCase(unittest.TestCase):
    """
    Test for sourcepath acquisition.
    """

    def test_registry_integration(self):
        # this package has defined no sources.
        sources = generate_scss_sourcepaths(['calmjs.sassy'])
        self.assertEqual({}, sources)

    def test_sourcepath_usage(self):
        from calmjs.registry import _inst
        from calmjs import dist

        # generate a dummy working set for a test dependency graph
        make_dummy_dist(self, (
            ('requires.txt', '\n'.join([
            ])),
        ), 'framework', '2.4')

        make_dummy_dist(self, (
            ('requires.txt', '\n'.join([
                'framework>=2.1',
            ])),
        ), 'widget', '1.1')

        make_dummy_dist(self, (
            ('requires.txt', '\n'.join([
                'framework>=2.2',
                'widget>=1.0',
            ])),
        ), 'forms', '1.6')

        make_dummy_dist(self, (
            ('requires.txt', '\n'.join([
                'framework>=2.1',
            ])),
        ), 'service', '1.1')

        make_dummy_dist(self, (
            ('requires.txt', '\n'.join([
                'framework>=2.1',
                'widget>=1.1',
                'forms>=1.6',
                'service>=1.1',
            ])),
        ), 'site', '2.0')

        working_set = WorkingSet([self._calmjs_testing_tmpdir])
        stub_item_attr_value(self, dist, 'default_working_set', working_set)

        dummy_regid = 'calmjs.sassy'
        self.addCleanup(_inst.records.pop, dummy_regid, None)
        # set up/register a dummy registry with dummy records.
        dummy_reg = _inst.records[dummy_regid] = SCSSRegistry(dummy_regid)
        dummy_reg.records = {
            'site': {
                'site/base': '/home/src/site/base.scss',
            },
            'widget': {
                'widget/ui': '/home/src/widget/ui.scss',
                'widget/widget': '/home/src/widget/widget.scss',
            },
            'forms': {
                'forms/ui': '/home/src/forms/ui.scss',
            },
            'service': {
                'service/lib': '/home/src/forms/lib.scss',
            },
        }
        dummy_reg.package_module_map = {
            'site': ['site'],
            'widget': ['widget'],
            'forms': ['forms'],
            'service': ['service'],
        }

        self.assertEqual({
            'site/base': '/home/src/site/base.scss',
            'widget/ui': '/home/src/widget/ui.scss',
            'widget/widget': '/home/src/widget/widget.scss',
            'service/lib': '/home/src/forms/lib.scss',
            'forms/ui': '/home/src/forms/ui.scss',
        }, generate_scss_sourcepaths(
            ['site'], registries=(dummy_regid,)
        ))

        self.assertEqual({
            'site/base': '/home/src/site/base.scss',
        }, generate_scss_sourcepaths(
            ['site'], registries=(dummy_regid,), method='explicit'
        ))

        self.assertEqual({
        }, generate_scss_sourcepaths(
            ['site'], registries=(dummy_regid,), method='none'
        ))
