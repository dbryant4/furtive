# Directory to create the virtual environment in
virtualenv_path=venv
PYTHONPATH=.

all:
	@echo "Use 'make test' to run Unit tests"
	@echo "Use 'make clean' to clean up temporary files"
	@echo "Use 'make install' to install the module system wide"
	@echo "Use 'make docs' to generate documentation"

tests: test
doc: docs

docs:
	$(virtualenv_path)/bin/pip install -r docs/requirements.txt
	mkdir -p docs/_static
	$(virtualenv_path)/bin/sphinx-build -b html docs/. ./docs/_build

test:
	mkdir -p test-results
	tox

lint: virtualenv package_install
	pylint --rcfile=.pylintrc furtive scripts --ignore=tests,venv

virtualenv:
	test -d $(virtualenv_path) || virtualenv $(virtualenv_path)
	$(virtualenv_path)/bin/pip install -U pip

clean:
	rm -rf furtive/*.pyc tests/*.pyc $(virtualenv_path) .coverage build docs/_build docs/_static test-results .tox
