from setuptools import setup, find_packages

version = '0.0.0'

classifiers = """
Development Status :: 1 - Planning
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
        'within the current Python environment.'
    ),
    long_description=long_description,
    classifiers=classifiers,
    keywords='',
    author='Tommy Yu',
    author_email='tommy.yu@auckland.ac.nz',
    url='https://github.com/calmjs/calmjs.sassy',
    license='gpl',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['calmjs'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'libsass',
        'calmjs>=3.2.0dev',
    ],
    extras_require={
    },
    calmjs_scss_module_registry=['calmjs.scss'],
    entry_points={
        'calmjs.registry': [
            'calmjs.scss = calmjs.sassy.registry:SCSSRegistry',
        ],
        'calmjs.runtime': [
            # 'sass = calmjs.sassy.runtime:default',
        ],
        'distutils.setup_keywords': [
            'calmjs_scss_module_registry = calmjs.dist:validate_line_list',
        ],
        'egg_info.writers': [
            ('calmjs_scss_module_registry.txt = '
                'calmjs.sassy.dist:write_module_registry_names'),
        ],
    },
    # test_suite="calmjs.sassy.tests.make_suite",
)
