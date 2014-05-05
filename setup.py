import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name = 'monscale',
    version = '0.11',
    packages = [
        "monscale", 
        "monscale.management", 
        "monscale.management.commands",
        "monscale.mappings",
        "monscale.pypelib",
        "monscale.pypelib.parsing",
        "monscale.pypelib.parsing.drivers",
        "monscale.pypelib.persistence",
        "monscale.pypelib.resolver",
        "monscale.pypelib.utils"
        ],
    include_package_data = False,
    license = 'BSD License',
    description = 'A Django app that monitor services and acts on them',
    long_description = README,
#TODO set the project's home page
    url = 'http://blog.digitalhigh.es',
    author = 'Javier Pardo Blasco(jpardobl)',
    author_email = 'jpardo@digitalhigh.es',
    extras_require = {
        "json": "simplejson"
        },
    install_requires = (
      "Django==1.6",
      "simplejson",
      'suds',
      "pyparsing",
      "pytz",
      "redis",
      "boto",
    ),
    entry_points={
        "console_scripts": [
            "evaluate_context = monscale.entrypoints:evaluate_context",
            "monscale_deploy = monscale.entrypoints:deploy",
                    ],
    },
    
  #  test_suite='test_project.tests.runtests',
   # tests_require=("selenium", "requests"),
    classifiers = [
        'Environment :: Web Environment',
        'Environment :: Console',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Systems Administration',
        'Topic :: System :: Monitoring',
        'Topic :: Utilities',
    ],
)
