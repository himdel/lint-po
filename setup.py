from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
  name="lint-po",
  description='A simple gettext .po linter to check for mangled variable names in translations',
  long_description=long_description,
  long_description_content_type='text/markdown',
  version="0.1.3",
  license='Apache License 2.0',
  packages=["lint_po"],
  scripts=["bin/lint-po"],
  url='https://github.com/himdel/lint-po',
)
