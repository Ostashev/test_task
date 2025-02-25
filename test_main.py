from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_status():
    response = client.get("/status")
    assert response.status_code == 200
    assert response.json() == {"status": "working"}

def test_create_task():
    with open("test_image.jpg", "rb") as image_file:
        response = client.post(
            "/task",
            files={"image": ("test_image.jpg", image_file, "image/jpeg")},
            data={"title": "Test Task"}
        )
    assert response.status_code == 200
    assert "task_id" in response.json()
    assert response.json()["status"] == "saved"

def test_get_task():
    with open("test_image.jpg", "rb") as image_file:
        create_response = client.post(
            "/task",
            files={"image": ("test_image.jpg", image_file, "image/jpeg")},
            data={"title": "Test Task"}
        )
    task_id = create_response.json()["task_id"]

    response = client.get(f"/task/{task_id}")
    assert response.status_code == 200
    assert response.headers["content-type"] in ["image/jpeg", "image/png"]

def test_get_task_not_found():
    response = client.get("/task/non_existent_task_id")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}
