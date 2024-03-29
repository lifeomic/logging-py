SHELL := /bin/bash
SRC := lifeomic_logging
PYTHONPATH := .
VENV := .venv
NOSE := env PYTHONPATH=$(PYTHONPATH) $(VENV)/bin/nosetests
FLAKE8 := env PYTHONPATH=$(PYTHONPATH) $(VENV)/bin/flake8
PYTHON := env PYTHONPATH=$(PYTHONPATH) $(VENV)/bin/python
BLACK := env PYTHONPATH=$(PYTHONPATH) $(VENV)/bin/black
PIP := $(VENV)/bin/pip3
VERSION := $(shell python -c "from $(SRC).version import __version__; print(__version__)")
REQUIREMENTS := -r requirements-dev.txt

default: clean test

clean:
	rm -rf build
	rm -rf dist
	rm -rf phc.egg-info

venv: $(VENV)/bin/activate
$(VENV)/bin/activate: requirements-dev.txt
	test -d $(VENV) || virtualenv -p python3 $(VENV)
	$(PIP) install -q $(REQUIREMENTS);
	touch $(VENV)/bin/activate

lint: venv
	$(FLAKE8) $(SRC)

format: venv
	$(BLACK) $(SRC)

test: lint
	$(NOSE) -v tests

package: venv
	$(PYTHON) setup.py sdist bdist_wheel

deploy: venv
	if [[ "$(shell $(PIP) index versions $(SRC))" == *$(VERSION)* ]]; then \
	  echo "Version $(VERSION) is already published, exiting"; \
	else \
	  echo "Now publishing version $(VERSION)" && $(PYTHON) -m twine upload dist/*; \
	fi


.PHONY: default venv requirements bootstrap lint test check package deploy
