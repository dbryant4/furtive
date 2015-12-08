# Directory to create the virtual environment in
virtualenv_path=venv
PYTHONPATH=.

all:
	@echo "Use 'make test' to run Unit tests"
	@echo "Use 'make clean' to clean up temporary files"
	@echo "Use 'make venv-install' to install the module in a local virtual environment"
	@echo "Use 'make install' to install the module system wide"
	@echo "Use 'make docs' to generate documentation"

tests: test
doc: docs

docs: venv-install
	$(virtualenv_path)/bin/pip install -r docs/requirements.txt
	mkdir -p docs/_static
	$(virtualenv_path)/bin/sphinx-build -b html docs/. ./docs/_build

install:
	python setup.py install

venv-install: test
	$(virtualenv_path)/bin/python setup.py install

test: virtualenv package_install lint
	$(virtualenv_path)/bin/nosetests --with-coverage --cover-package=furtive -v

lint: virtualenv package_install
	pylint --rcfile=.pylintrc furtive scripts --ignore=tests,venv

package_install: virtualenv
	$(virtualenv_path)/bin/pip install -r requirements.txt

virtualenv:
	test -d $(virtualenv_path) || virtualenv $(virtualenv_path)

clean:
	rm -rf furtive/*.pyc tests/*.pyc $(virtualenv_path) .coverage build docs/_build docs/_static
