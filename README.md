# LifeOmic Python Logging

## Project Status

![GitHub](https://img.shields.io/github/license/lifeomic/logging-py.svg?style=for-the-badge)
![PyPI status](https://img.shields.io/pypi/status/lifeomic_logging.svg?style=for-the-badge)
![Downloads](https://img.shields.io/pypi/dw/lifeomic_logging?style=for-the-badge)
![GitHub release](https://img.shields.io/github/release/lifeomic/logging-py.svg?style=for-the-badge)

## Getting Started

### Dependencies

- [Python 3](https://www.python.org/download/releases/3.0/) version >= 3.6

### Getting the Source

This project is [hosted on GitHub](https://github.com/lifeomic/logging-py). You
can clone this project directly using this command:

```bash
git clone git@github.com:lifeomic/logging-py.git
```

### Development

Python environments are managed using
[virtualenv](https://virtualenv.pypa.io/en/latest/). Be sure to have this
installed first `pip install virtualenv`. The makefile will setup the
environment for the targets listed below.

#### Running tests

```bash
make test
```

#### Linting

```bash
make lint
```

### Installation

```bash
pip3 install lifeomic_logging
```

### Usage

```python
from lifeomic_logging import scoped_logger

with scoped_logger(__name__, { "bar": "foo" }) as log:
  log.info("message")
```

## Release Process

[Releases](https://github.com/lifeomic/logging-py/releases) are generally
created with each merged PR. Packages for each release are published to
[PyPi](https://pypi.org/project/phc/). See [CHANGELOG.md](CHANGELOG.md) for
release notes.

To release a new version of the package, update the version number in
`lifeomic_logging/version.py` as a part of your change, and the new version will
be released automatically to PyPi on merge.

### Versioning

This project uses [Semantic Versioning](http://semver.org/).

## Contributing

We encourage public contributions! Please review
[CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
for details on our code of conduct and development process.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for
details.

## Authors

See the list of [contributors](https://github.com/lifeomic/cli/contributors) who
participate in this project.
