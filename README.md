# smartsquash

[![PyPI](https://badge.fury.io/py/smartsquash.svg)](https://badge.fury.io/py/smartsquash)
[![PyPI - License](https://img.shields.io/pypi/l/smartsquash.svg)](https://github.com/max-wittig/smartsquash/blob/master/LICENSE)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

> This is still in testing phase.

Makes daily git workflows easier, automates rebases or fixups.

### build

```sh
poetry install --no-dev --no-root
poetry build
```

### installation

```sh
pip3 install smartsquash
```

### usage

```sh
usage: sq [-h] [--target-branch TARGET_BRANCH] [--repo REPO] [--dry] [-s] [--no-add]

optional arguments:
  -h, --help            show this help message and exit
  --target-branch TARGET_BRANCH
                        Specify branch to target. Default is 'master'
  --repo REPO           Specify repo to modify. Uses pwd by default
  --dry                 Run dry
  -s, --squash          Squash similar commits on your feature branch
  --no-add              Don't add modified files to staging area
```

### run tests

```sh
poetry run coverage run --source . -m pytest  
poetry run coverage report
```
