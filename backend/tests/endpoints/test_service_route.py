from http import HTTPStatus


def test_health_route(client):
    url = _get_url = "/api/v1/health"
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK, response.json()
    assert response.json() == {"message": "pong"}
