import json
from endusersfixture import *

from generate_randomized_data import GenerateRestPayload

# Todo: implement logging of data objects from failed test runs to a file
# Todo: code coverage metrics

@pytest.mark.parametrize('user_login', ['superuser_client', 'agent_client', 'end_user_client','end_user_client2'], scope="class")
@pytest.mark.usefixtures('user')
class TestCreateUsers:
    """Test permissions of different user permissions levels to create and view end users"""
    @pytest.mark.usefixtures('create_end_user')
    def test_user_create_end_user_if_allowed(self, create_end_user, user):
        response = create_end_user
        if user['level'] == 'superuser':
            assert response.status_code == 201
        else:
            assert response.status_code == 403

    def test_user_get_end_users_if_allowed(self, user):
        # Return unauthorized if invalid token
        response = requests.get(pytest.base_url + '/api/endusers/', headers={'Authorization': 'Token notatoken'})
        assert response.status_code == 401

        # show all end users if correct token and privilege level
        response = requests.get(pytest.base_url + '/api/endusers/', headers=user['auth'])

        if (user['level'] == 'superuser'):
            assert response.status_code == 200
            end_users = json.loads(response.content)
            assert 'count' in end_users # additional assertion that response not broken and falsely reporting success # Todo: further testing beyond MVP core tests to properly safeguard against this
        else:
            assert response.status_code == 403

    @pytest.mark.skip(reason= "Todo: Disabled until fix known TRANSIENT bug where superuser is not detecting manually created end users and returns 404: Not Found. Also expand this test to accommodate new non-superuser scenarios")
    def test_user_get_individual_end_user_if_allowed(self, user, request):
        # Return unauthorized if invalid token
        end_user_id = request.getfixturevalue('end_user_client')['id']

        response = requests.get(pytest.base_url + '/api/endusers/' + str(end_user_id) + '/', headers={'Authorization': 'Token notatoken'})
        assert response.status_code == 401

        # show end user if correct token
        response = requests.get(pytest.base_url + '/api/endusers/' + str(end_user_id) + '/', headers=user['auth'])
        assert response.status_code == 200      # Todo: fix bug where superuser is not detecting manually created end users

        found_end_user = json.loads(response.content)
        assert found_end_user['id'] == end_user_id

        # Todo: Add testing for non-superusers now this test has been expanded and then re-enable test

    def test_user_create_agent_if_allowed(self, user):
        url = pytest.base_url + '/api/company-manager/'
        payload = (GenerateRestPayload(user['token'], "Post", url)).payload

        response = requests.post(url, headers=user['auth'], data=payload)

        if (user['level'] == 'superuser'):
            assert response.status_code == 201
        else:
            assert response.status_code == 403
