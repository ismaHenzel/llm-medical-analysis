from http import HTTPStatus


def test_get_token(client, patient):
    response = client.post(
        '/auth/token',
        data={'username': patient.email, 'password': patient.clean_password},
    )
    token = response.json()
    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token
