# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os import makedirs
from os.path import join

from pkg_resources import get_distribution
from pkg_resources import WorkingSet

from calmjs.registry import get as get_registry
from calmjs.testing import utils
from calmjs import dist as calmjs_dist


def setup_class_integration_environment(cls, registry_name='calmjs.scss'):
    from calmjs import base

    cls.registry_name = registry_name
    cls.dist_dir = utils.mkdtemp_realpath()
    # fake node_modules for transpiled sources
    cls._nm_root = join(cls.dist_dir, 'fake_modules')
    cls._ep_root = join(cls.dist_dir, 'example', 'package')
    makedirs(cls._ep_root)
    makedirs(cls._nm_root)

    index_scss = join(cls._ep_root, 'index.scss')
    with open(index_scss, 'w') as fd:
        fd.write(
            '@import "example/package/colors";\n'
            'body { background-color: $theme_color; }\n'
        )

    colors_scss = join(cls._ep_root, 'colors.scss')
    with open(colors_scss, 'w') as fd:
        fd.write(
            '$theme_color: #f00;\n'
        )

    # a dummy scss source from "node_modules"
    mockstrap = join(cls._nm_root, 'mockstrap.scss')
    with open(mockstrap, 'w') as fd:
        fd.write('')

    # JavaScript import/module names to filesystem path.
    # Normally, these are supplied through the calmjs setuptools
    # integration framework.
    cls._example_package_map = {
        'example/package/index': index_scss,
        'example/package/colors': colors_scss,
    }

    # also add a proper mock distribution for this.
    utils.make_dummy_dist(None, (
        ('requires.txt', ''),
        ('calmjs_scss_module_registry.txt', cls.registry_name),
        ('entry_points.txt', (
            '[%s]\n'
            'example.package = example.package\n' % cls.registry_name
        )),
    ), 'example.package', '1.0', working_dir=cls.dist_dir)

    # create a separate package that reuse the first one

    cls._ep_usage = join(cls.dist_dir, 'example', 'usage')
    makedirs(cls._ep_usage)

    # for testing loading of data provided by a test
    usage_index_scss = join(cls._ep_usage, 'index.scss')
    with open(usage_index_scss, 'w') as fd:
        fd.write('@import "example/package/colors";\n')
        fd.write('body { color: $theme_color; }\n')

    utils.make_dummy_dist(None, (
        ('requires.txt', 'example.package'),
        ('entry_points.txt', (
            '[calmjs.artifacts]\n'
            'styles.css = calmjs.sassy.artifact:complete_css\n'
            '[%s]\n'
            'example.usage = example.usage\n' % cls.registry_name
        )),
    ), 'example.usage', '1.0', working_dir=cls.dist_dir)

    # finally, include the entry_point information for calmjs.sassy
    # to ensure correct function of certain default registries.
    utils.make_dummy_dist(None, (
        ('requires.txt', ''),
        ('entry_points.txt', (
            get_distribution('calmjs.sassy').get_metadata('entry_points.txt')
        )),
    ), 'calmjs.sassy', '0.0', working_dir=cls.dist_dir)

    working_set = WorkingSet([cls.dist_dir])
    cls.root_working_set, calmjs_dist.default_working_set = (
        calmjs_dist.default_working_set, working_set)
    base.working_set = working_set

    # manual registry creation
    registry = get_registry(cls.registry_name)
    registry.package_module_map['example.package'] = ['example.package']
    registry.records['example.package'] = cls._example_package_map
    registry.package_module_map['example.usage'] = ['example.usage']
    registry.records['example.usage'] = {
        'example/usage/index': usage_index_scss,
    }


def teardown_class_integration_environment(cls):
    from calmjs.registry import _inst
    from calmjs import base
    from calmjs import dist as calmjs_dist

    _inst.records.pop(cls.registry_name, None)
    _inst.records.pop('calmjs.artifacts', None)
    utils.rmtree(cls.dist_dir)
    calmjs_dist.default_working_set = cls.root_working_set
    base.working_set = cls.root_working_set
