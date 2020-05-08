
def test_simulate_endpoint(client, simulation_schema):
    sir_splitted_schema = simulation_schema("SplittedSEIR.json")

    mimetype = "application/json"
    url = "/simulate/sir_splitted"

    response = client.post(
        url,
        json=sir_splitted_schema,
        content_type=mimetype
    )

    assert response.json
    assert response.status_code == 200
    assert response.json
