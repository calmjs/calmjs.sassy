from setuptools import setup, find_packages

version = '1.0.1'

classifiers = """
Development Status :: 5 - Production/Stable
Environment :: Console
Environment :: Plugins
Framework :: Setuptools Plugin
Intended Audience :: Developers
License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)
Operating System :: MacOS :: MacOS X
Operating System :: Microsoft :: Windows
Operating System :: POSIX
Operating System :: POSIX :: BSD
Operating System :: POSIX :: Linux
Operating System :: OS Independent
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3
Programming Language :: Python :: 3.3
Programming Language :: Python :: 3.4
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6
Programming Language :: Python :: Implementation :: CPython
Programming Language :: Python :: Implementation :: PyPy
Topic :: Software Development :: Build Tools
Topic :: System :: Software Distribution
Topic :: Utilities
""".strip().splitlines()

long_description = (
    open('README.rst').read()
    + '\n' +
    open('CHANGES.rst').read()
    + '\n')

setup(
    name='calmjs.sassy',
    version=version,
    description=(
        'Package for extending the Calmjs framework to support the usage of '
        'sass in a manner that crosses Python package boundaries by exposing '
        'an import system that mimics the package namespaces available '
        'within a given Python environment.'
    ),
    long_description=long_description,
    classifiers=classifiers,
    keywords='',
    author='Tommy Yu',
    author_email='tommy.yu@auckland.ac.nz',
    url='https://github.com/calmjs/calmjs.sassy',
    license='GPL',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['calmjs'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'calmjs>=3.2.0',
    ],
    extras_require={
        'libsass': [
            'libsass>=0.11.0',
        ],
    },
    calmjs_scss_module_registry=['calmjs.scss'],
    entry_points={
        'calmjs.registry': [
            'calmjs.scss = calmjs.sassy.registry:SCSSRegistry',
        ],
        'calmjs.runtime': [
            'scss = calmjs.sassy:libsass_runtime',
        ],
        'distutils.setup_keywords': [
            'calmjs_scss_module_registry = calmjs.dist:validate_line_list',
            'extras_calmjs_scss = calmjs.dist:validate_json_field',
        ],
        'egg_info.writers': [
            ('extras_calmjs_scss.json = '
                'calmjs.sassy.dist:write_extras_calmjs_scss'),
            ('calmjs_scss_module_registry.txt = '
                'calmjs.sassy.dist:write_module_registry_names'),
        ],
    },
    test_suite="calmjs.sassy.tests.make_suite",
)
