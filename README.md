# smartsquash

> This is still in testing phase.

Makes daily git workflows easier, automates rebases or fixups.

### build

```sh
poetry install --no-dev --no-root
poetry build
```

### installation

```sh
pip3 install dist/smartsquash-0.1.0-py3-none-any.whl
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
