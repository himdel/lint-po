from setuptools import setup

setup(
  name="lint-po",
  description='A simple gettext .po linter to check for mangled variable names in translations',
  version="0.1.0",
  license='Apache License 2.0',
  py_modules=["lint_po"],
  scripts=["bin/lint-po"],
)
