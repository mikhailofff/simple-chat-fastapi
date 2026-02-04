from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_ws(app: FastAPI) -> None:
    client1 = TestClient(app)
    client2 = TestClient(app)

    with client1.websocket_connect("/api/ws?username=testname1") as websocket1:
        data1 = websocket1.receive_json()
        assert data1["userlist"] == ["testname1"]

        with client2.websocket_connect("/api/ws?username=testname2") as websocket2:
            data1 = websocket1.receive_json()
            data2 = websocket2.receive_json()

            assert data1["userlist"] == ["testname1", "testname2"]
            assert data2["userlist"] == ["testname1", "testname2"]

            websocket2.send_text("Hello there")
            websocket2.receive_text()
            received_text1 = websocket1.receive_text()

            websocket1.send_text("Hi")
            websocket1.receive_text()
            received_text2 = websocket2.receive_text()

            assert received_text1 == "Hello there"
            assert received_text2 == "Hi"

        data1 = websocket1.receive_json()
        assert data1["userlist"] == ["testname1"]
