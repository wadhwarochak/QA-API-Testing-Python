
import requests

from helpers import (
    create_task,
    update_task,
    get_task,
    list_tasks,
    delete_task,
    new_task_payload,
    ENDPOINT
)


def test_can_call_endpoint():
    response = requests.get(ENDPOINT)
    assert response.status_code == 200


def test_can_create_task():
    payload = new_task_payload()

    create_task_response = create_task(payload)
    assert create_task_response.status_code == 200

    data = create_task_response.json()
    task_id = data["task"]["task_id"]

    get_task_response = get_task(task_id)
    assert get_task_response.status_code == 200

    get_task_data = get_task_response.json()

    assert get_task_data["content"] == payload["content"]
    assert get_task_data["user_id"] == payload["user_id"]


def test_can_update_task():
    # Create a task
    payload = new_task_payload()
    create_task_response = create_task(payload)
    assert create_task_response.status_code == 200

    task_id = create_task_response.json()["task"]["task_id"]

    # Update the task
    new_payload = {
        "user_id": payload["user_id"],
        "task_id": task_id,
        "content": "my updated content",
        "is_done": True,
    }

    update_task_response = update_task(new_payload)
    assert update_task_response.status_code == 200

    # Get and validate the changes
    get_task_response = get_task(task_id)
    assert get_task_response.status_code == 200

    get_task_data = get_task_response.json()

    assert get_task_data["content"] == new_payload["content"]
    assert get_task_data["is_done"] == new_payload["is_done"]


def test_can_list_users():
    # Create N tasks
    n = 3
    payload = new_task_payload()

    for _ in range(n):
        create_task_response = create_task(payload)
        assert create_task_response.status_code == 200

    # List tasks and check count
    user_id = payload["user_id"]

    list_task_response = list_tasks(user_id)
    assert list_task_response.status_code == 200

    data = list_task_response.json()
    tasks = data["tasks"]

    assert len(tasks) == n


def test_can_delete_task():
    # Create a task
    payload = new_task_payload()
    create_task_response = create_task(payload)
    assert create_task_response.status_code == 200

    task_id = create_task_response.json()["task"]["task_id"]

    # Delete the task
    delete_task_response = delete_task(task_id)
    assert delete_task_response.status_code == 200

    # Verify task is deleted
    get_task_response = get_task(task_id)
    assert get_task_response.status_code == 404
