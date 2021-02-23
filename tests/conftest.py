import pytest
import os
from time import sleep


# @pytest.fixture(autouse=True)
# def run_around_tests():
#     os.system(
#         'docker run --name test-postgres '
#         '-e POSTGRES_PASSWORD=mysecretpassword '
#         '-e POSTGRES_DB=postgres -d -p 5432:5432 postgres'
#     )
#     sleep(1)
#     os.system('poetry run alembic upgrade head')
#     yield
#     os.system('docker kill test-postgres')
#     os.system('docker rm test-postgres')