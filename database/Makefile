APP_NAME = story_game
APP_AUTHOR = vaclav-v

FILE_VSCODE_SETTINGS = .vscode/settings.json

define VSCODE_SETTINGS
echo "{" >> $(FILE_VSCODE_SETTINGS)
echo "\"python.pythonPath\": \".venv/bin/python\"," >> $(FILE_VSCODE_SETTINGS)
echo "\"python.linting.pylintEnabled\": false," >> $(FILE_VSCODE_SETTINGS)
echo "\"python.linting.flake8Enabled\": true," >> $(FILE_VSCODE_SETTINGS)
echo "\"python.linting.mypyEnabled\": true," >> $(FILE_VSCODE_SETTINGS)
echo "\"python.linting.enabled\": true," >> $(FILE_VSCODE_SETTINGS)
echo "\"python.testing.pytestArgs\": [" >> $(FILE_VSCODE_SETTINGS)
echo "\"tests\"" >> $(FILE_VSCODE_SETTINGS)
echo "]," >> $(FILE_VSCODE_SETTINGS)
echo "\"python.testing.unittestEnabled\": false," >> $(FILE_VSCODE_SETTINGS)
echo "\"python.testing.nosetestsEnabled\": false," >> $(FILE_VSCODE_SETTINGS)
echo "\"python.testing.pytestEnabled\": true" >> $(FILE_VSCODE_SETTINGS)
echo "}" >> $(FILE_VSCODE_SETTINGS)

endef


FILE_GITIGNORE = .gitignore

define GITIGNORE
echo ".venv" >> $(FILE_GITIGNORE)
echo ".vscode" >> $(FILE_GITIGNORE)
echo "*_cache" >> $(FILE_GITIGNORE)
echo "__pycache__" >> $(FILE_GITIGNORE)
echo ".python-version" >> $(FILE_GITIGNORE)

endef


FILE_SETUP = setup.cfg

define SETUP
echo "[flake8]" >> $(FILE_SETUP)
echo "ignore = DAR201, DAR101, WPS407" >> $(FILE_SETUP)

endef


init:
	pyenv local 3.8.3
	poetry init -n --name $(APP_NAME) --author $(APP_AUTHOR)
	poetry add --dev wemake-python-styleguide
	poetry add --dev mypy
	poetry add --dev pytest
	poetry add --dev pytest-cov
	mkdir .vscode
	touch $(FILE_VSCODE_SETTINGS)
	$(VSCODE_SETTINGS)
	touch $(FILE_GITIGNORE)
	$(GITIGNORE)
	touch $(FILE_SETUP)
	$(SETUP)
	mkdir $(APP_NAME)
	touch $(APP_NAME)/__init__.py
	echo '"""Main module $(APP_NAME) project."""' > $(APP_NAME)/__init__.py
	mkdir tests
	touch tests/__init__.py
	echo '"""Tests for $(APP_NAME)."""' > tests/__init__.py
	touch tests/test_$(APP_NAME).py
	poetry shell

lint:
	poetry run flake8 $(APP_NAME)
	poetry run flake8 data_base
	poetry run mypy $(APP_NAME)
	poetry run mypy data_base

install:
	poetry install

test:
	poetry run pytest tests/

pr_test:
	docker run --name test-postgres -e POSTGRES_PASSWORD=mysecretpassword -e POSTGRES_DB=postgres -d -p 5432:5432 postgres
	sleep 1
	poetry run alembic upgrade head

stop_test_base:
	docker kill test-postgres
	docker rm test-postgres

test-vv:
	poetry run pytest -vv tests/
package-install:
	python3 -m pip -q install poetry
	poetry build -q
	python3 -m pip -q install --user dist/*.whl
coverage:
	poetry run pytest --cov=$(APP_NAME) --cov-report xml tests/

sqlalchemy-init:
	poetry add sqlalchemy
	poetry add psycopg2-binary
	poetry add alembic
	poetry run alembic init alembic
	echo 'exclude = alembic/*' >> setup.cfg
	touch $(APP_NAME)/models.py
	poetry add --dev sqlalchemy-stubs
	echo '"""DataBase models."""' >> $(APP_NAME)/models.py
	echo '[mypy]' >> setup.cfg
	echo 'plugins = sqlmypy' >> setup.cfg
db_revision:
	poetry run alembic revision --autogenerate

db_update:
	poetry run alembic upgrade head

run:
	poetry run uvicorn data_base.main:app --reload

req:
	poetry export>requirements.txt