import pytest
import os
import json
from src.app import create_app

@pytest.fixture
def app():
    ''' create n config a flask app for testing'''
    app = create_app()
    app.config.update({
        "TESTING" : True,
        "JWT_SECRET_KEY" : "test-jwt-key",
        "DATA_FODLER" : os.path.join(os.path.dirname(__file__), "test_data")
    })

    # create a test data dir
    os.makedirs(app.config['DATA_FODLER'], exist_ok=True)

    yield app

    #clean up tData
    for file in ["users.json", "accounts.json", "transactions.json", "loans.json"]:
        file_path = os.path.join(app.config['DATA_FODLER'], file)
        if os.path.exists(file_path):
            os.remove(file_path)


@pytest.fixture
def client(app):
    ''' test client for the app '''
    return app.test_client()

@pytest.fixture
def auth_header(client):
    ''' getting auth headers for tUser '''
    client.post("api/v1/users/register", json={
        "username": "tAdmin",
        "password": "pwd123",
        "email": "tadmin@exmaple.com",
        "full_name" : "T Admin",
        "role" : "admin"
    })

    resp = client.post("api/v2/users/login", json={
        "username": "tAdmin",
        "password": "pwd123",
    })

    data = json.loads(resp.data)
    return {"Authorization": f"Bearer {data['token']}"}