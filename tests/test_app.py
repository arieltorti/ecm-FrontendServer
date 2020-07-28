def test_simulate_endpoint(app):
    simSIR = {
        "step": 5,
        "days": 50,
        "initial_conditions": {"S": 999900, "I": 100, "R": 0},
        "params": {"beta": 0.22, "gamma": 0.0714},
    }

    mimetype = "application/json"
    url = "/simulate/1"
    with app.test_client() as client:
        app.config["WTF_CSRF_ENABLED"] = False

        response = client.post(url, json=simSIR, content_type=mimetype)
        assert response.json
        assert response.status_code == 200
