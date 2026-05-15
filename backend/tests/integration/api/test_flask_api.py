# Test di integrazione per le rotte HTTP Flask.
import pytest
import mongomock
from unittest.mock import patch

@pytest.fixture
def flask_app(mongo_db):
    standard_doc = {
        "_id": "STD-001",
        "name": "Test Standard",
        "version_number": "1.0",
        "requirements": [
            {
                "id": "REQ-001",
                "name": "Requisito 1",
                "description": {
                    "norm_description": "Desc 1",
                    "target_description": "Target 1",
                },
                "dependency_ids": [],
                "decision_tree": {
                    "root_node_id": "N1",
                    "nodes": [
                        {
                            "node_id": "N1",
                            "node_type": "decision_node",
                            "question": "Domanda 1",
                            "child_yes": "L_PASS",
                            "child_no": "L_FAIL",
                        },
                        {"node_id": "L_PASS", "node_type": "leaf_node", "verdict": "pass"},
                        {"node_id": "L_FAIL", "node_type": "leaf_node", "verdict": "fail"},
                    ],
                },
            },
            {
                "id": "REQ-002",
                "name": "Requisito 2",
                "description": {
                    "norm_description": "Desc 2",
                    "target_description": "Target 2",
                },
                "dependency_ids": ["REQ-001"],
                "decision_tree": {
                    "root_node_id": "N1",
                    "nodes": [
                        {
                            "node_id": "N1",
                            "node_type": "decision_node",
                            "question": "Domanda 2",
                            "child_yes": "L_PASS",
                            "child_no": "L_FAIL",
                        },
                        {"node_id": "L_PASS", "node_type": "leaf_node", "verdict": "pass"},
                        {"node_id": "L_FAIL", "node_type": "leaf_node", "verdict": "fail"},
                    ],
                },
            },
        ],
    }
    mongo_db["compliance_standards"].insert_one(standard_doc)
    with patch(
        "infrastructure.database.connection.connect",
        return_value=(mongomock.MongoClient(), mongo_db),
    ):
        from app import create_app
        app = create_app()
        app.config["TESTING"] = True
        app.config["PROPAGATE_EXCEPTIONS"] = False
        yield app

@pytest.fixture
def client(flask_app):
    return flask_app.test_client()

# test api-device
def _create_device(client, name="Test Router", standard_id="STD-001"):
    return client.post("/devices", json={
        "device_name": name,
        "device_os": "OpenWRT",
        "device_description": "Device di test",
        "standard_id": standard_id,
    })


def _open_session(client, device_id):
    return client.post("/sessions", json={"device_id": device_id})

class TestApiDevice:

    def test_create_device(self, client):
        resp = _create_device(client)
        assert resp.status_code == 201
        assert "device_id" in resp.get_json()

    def test_create_device_body_mancante(self, client):
        resp = client.post("/devices", data="non-json", content_type="text/plain")
        assert resp.status_code == 415

    def test_update_device(self, client):
        device_id = _create_device(client).get_json()["device_id"]
        resp = client.put(f"/devices/{device_id}", json={
            "device_name": "Router Aggiornato",
            "device_os": "OpenWRT",
            "device_description": "Descrizione aggiornata",
        })
        assert resp.status_code == 200

    def test_update_device_inesistente(self, client):
        resp = client.put("/devices/id-inesistente", json={
            "device_name": "X",
            "device_os": "Linux",
            "device_description": "Desc",
        })
        assert resp.status_code == 404

    def test_delete_device(self, client):
        device_id = _create_device(client).get_json()["device_id"]
        resp = client.delete(f"/devices/{device_id}")
        assert resp.status_code == 204

    def test_delete_device_inesistente(self, client):
        resp = client.delete("/devices/id-inesistente")
        assert resp.status_code == 404

# test api-valutazione
class TestApiSessioneValutazione:

    def test_open_session(self, client):
        device_id = _create_device(client).get_json()["device_id"]
        resp = _open_session(client, device_id)
        assert resp.status_code == 200
        assert "session_id" in resp.get_json()

    def test_get_active_session(self, client):
        device_id = _create_device(client).get_json()["device_id"]
        session_id = _open_session(client, device_id).get_json()["session_id"]
        resp = client.get("/sessions/active")
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["session_id"] == session_id
        assert body["device_id"] == device_id

    def test_get_active_session_204(self, client):
        resp = client.get("/sessions/active")
        assert resp.status_code == 204

    def test_close_session(self, client):
        device_id = _create_device(client).get_json()["device_id"]
        session_id = _open_session(client, device_id).get_json()["session_id"]
        resp = client.delete(f"/sessions/{session_id}")
        assert resp.status_code == 200
        assert client.get("/sessions/active").status_code == 204

    def test_commit_session(self, client):
        device_id = _create_device(client).get_json()["device_id"]
        session_id = _open_session(client, device_id).get_json()["session_id"]
        resp = client.post(f"/sessions/{session_id}/commit")
        assert resp.status_code == 200

    def test_commit_and_close(self, client):
        device_id = _create_device(client).get_json()["device_id"]
        session_id = _open_session(client, device_id).get_json()["session_id"]
        resp = client.post(f"/sessions/{session_id}/commit-and-close")
        assert resp.status_code == 200
        assert client.get("/sessions/active").status_code == 204