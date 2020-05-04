
def test_simulate_endpoint(client, sir_splitted_schema):
    mimetype = "application/json"
    url = "/simulate/sir_splitted"
    response = client.post(url, json=sir_splitted_schema, content_type=mimetype)
    assert response.status_code == 200
