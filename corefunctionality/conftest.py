import os
# from django import setup
from loginsfixture import *


def pytest_configure():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings.local')

   # setup()
    pytest.base_url = 'http://localhost:8000'
    # pytest.users = # import file (dictionary of config items)

# Todo: generator
# def pytest_generate_tests(metafunc):
#     if metafunc.function.__name__ == 'test_one':
#         params = ['A']
#     else:
#         params = ['B']
#
#     metafunc.parametrize('heavy_fixture', params, scope="function", indirect=True)
