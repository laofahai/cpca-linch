# -*- coding: utf-8 -*-
from setuptools import setup
from pathlib import Path
import ast
import os

# Read the literal version without importing runtime code during isolated builds.
module = ast.parse(Path(__file__).with_name("cpca").joinpath("__init__.py").read_text(encoding="utf-8"))
version = next(ast.literal_eval(node.value) for node in module.body
               if isinstance(node, ast.Assign)
               and any(isinstance(t, ast.Name) and t.id == "VERSION" for t in node.targets))


def read_rst(f):
    return open(f, 'r', encoding='utf-8').read()


README = os.path.join(os.path.dirname(__file__), 'README.rst')

requires = [
           'pandas',
           'jieba',
           'setuptools<82',  # jieba 0.42.1 imports pkg_resources
           ]  


setup(name='cpca-linch',
      version=".".join(map(str, version)),
      python_requires=">=3.8",
      description='Chinese Province, City and Area Recognition Utilities (2026 data snapshot)',
      long_description=read_rst(README),
      author='laofahai',
      author_email='',
      url='https://github.com/laofahai/cpca-linch',
      license="MIT",
      classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Natural Language :: Chinese (Simplified)',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Indexing',
      ],
      keywords='Simplified Chinese,Chinese geographic information,Chinese province city area recognition',
      packages=['cpca', 'cpca.resources'],
      package_dir={'cpca': 'cpca', 'cpca.resources': 'cpca/resources'},
      package_data={'': ['*.csv']},
      include_package_data=True,
      install_requires=requires,
)
