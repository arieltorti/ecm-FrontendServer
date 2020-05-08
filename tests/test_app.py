
def test_simulate_endpoint(client, simulation_schema):
    sir_splitted_schema = simulation_schema("SEIR.json")

    mimetype = "application/json"
    url = "/simulate/1"

    response = client.post(
        url,
        json=sir_splitted_schema,
        content_type=mimetype
    )
    assert response.json
    assert response.status_code == 200
