import pytest

@pytest.fixture(scope="module")
def superuser_client():
    usr = pytest.users['superuser']
    login = {
        'level': 'superuser',
        'username' : usr['username'],
        'email' : usr['email'],
        'password' : usr['password'],
        'token' : usr['token'],
        'agentId': usr['agentId']
    }
    login['authorization'] = 'Token {}'.format(login['token'])
    login['auth'] = {'Authorization': login['authorization']}

    return login

@pytest.fixture(scope="module")
def agent_client():
    usr = pytest.users['agent']
    login = {
        'level': 'agent',
        'username' : usr['username'],
        'email' : usr['email'],
        'password' : usr['password'],
        'token' : usr['token'],
        'agentId': usr['agentId']
    }
    login['authorization'] = 'Token {}'.format(login['token'])
    login['auth'] = {'Authorization': login['authorization']}

    return login

@pytest.fixture(scope="module")
def end_user_client():
    usr = pytest.users['end_user']
    login = {
        'level': 'end_user',
        'username' : usr['username'],
        'email' : usr['email'],
        'password' : usr['password'],
        'token' : usr['token'],
        'agentId': usr['agentId']
    }
    login['authorization'] = 'Token {}'.format(login['token'])
    login['auth'] = {'Authorization': login['authorization']}

    return login

@pytest.fixture(scope="module")
def end_user_client2():
    usr = pytest.users['end_user2']
    login = {
        'level': 'end_user',
        'username' : usr['username'],
        'email' : usr['email'],
        'password' : usr['password'],
        'token' : usr['token'],
        'agentId': usr['agentId']
    }
    login['authorization'] = 'Token {}'.format(login['token'])
    login['auth'] = {'Authorization': login['authorization']}

    return login

@pytest.fixture(scope="class")
def no_client():
    login = {
        'level'    : 'no_client',
        'username' : '',
        'email' : '',
        'password' : '',
        'token' : '	',
        'id'    : ''
    }
    login['auth'] = ''

    return login

@pytest.fixture(scope="class")
def randomised_end_user_client(superuser_client, create_end_user, request): # Todo: add D.O.B
    response = request.getfixturevalue('create_end_user')

    assert response.status_code == 201

    end_user = json.loads(response.content)

    cursor = connection.cursor()
#, auth_user.password
    query = """
    select authtoken_token.key, auth_user.password from authtoken_token
    left join auth_user
    on authtoken_token.user_id = auth_user.id
    where auth_user.id = {}
    """.format(end_user['id'])


    cursor.execute(query)
    end_user_sensitive = cursor.fetchone()

    login = {
        'level': 'end_user',
        'username': end_user['username'],
        'email': end_user['email'],
        'password': end_user_sensitive[1],
        'token': end_user_sensitive[0],
        'id': end_user['id']
    }
    login['authorization'] = 'Token {}'.format(login['token'])
    login['auth'] = {'Authorization': login['authorization']}

    return login

# instantiates a requested user login for a collection of tests
@pytest.fixture(scope="class")
def user (user_login, request):    # specify fixture to use as param
    # if user_login == 'randomised_end_user_client':       # Todo: as above re-enable
    #     user = request.getfixturevalue('randomised_end_user_client')
    # else:
    user = request.getfixturevalue(user_login)
    return user

#todo put agent IDs in a separate fixture for passed-in data
