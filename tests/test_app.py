def test_simulate_endpoint(client):
    simSIR = {
        "step": 5,
        "days": 50,
        "initial_conditions": {"S": 999600, "I": 400, "R": 0},
        "params": {"beta": 1, "gamma": 0.0714},
    }

    mimetype = "application/json"
    url = "/simulate/8"
    response = client.post(url, json=simSIR, content_type=mimetype)
    assert response.json
    assert response.status_code == 200
