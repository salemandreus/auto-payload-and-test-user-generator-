import pytest
import requests
from generate_randomized_data import GenerateRestPayload
from time import localtime, strftime, sleep


@pytest.fixture(scope="class")
def create_end_user(user_login, request):
    """ This fixture creates a randomised end-user. The login of the creator is passed in via the user_login fixture to facilitate testing create permissions of different permission levels on rest calls, ie this is not only used as a factory fixture."""
    # post end users
    url =pytest.base_url + '/api/endusers/'
    user = request.getfixturevalue(user_login)

    for reattempts in range(3):
        payload = (GenerateRestPayload(user['token'], "Post", url)).payload

        response = requests.post(url, headers=user['auth'], data=payload)       # Todo - investigate intermittent failure of the server-side API we are testing in generating user accounts
        if response.status_code != 400:                                             # current workaround is to reattempt user creation as the server-side user creation bug on the API is intermittent
            break
        sleep(1)

    return response
