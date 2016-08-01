"""Test amazon turk views.
"""


def test_register(client, users):
    response = client.get("/mturk/register?foo=bar")
    assert response.status_code == 200
    assert "foo" in response.data
    assert "bar" in response.data
