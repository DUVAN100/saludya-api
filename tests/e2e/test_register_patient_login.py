from fastapi.testclient import TestClient


def test_register_patient_and_login(client: TestClient):
    payload = {
        "email": "e2e.patient@test.com",
        "password": "Password123!",
        "first_name": "Paula",
        "last_name": "Gomez",
        "birth_date": "1992-10-10",
        "phone": "3009876543",
        "document_number": "PAT-100",
        "document_type": "CC",
        "gender": "F",
        "address": "Carrera 5",
    }

    register_response = client.post("/api/v1/patients", json=payload)
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    assert login_response.status_code == 200
    assert login_response.json()["access_token"]
