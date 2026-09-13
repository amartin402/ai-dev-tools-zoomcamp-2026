from fastapi.testclient import TestClient

from app.main import app
from app.models import CreateBoardRequest
from app.store import DatabaseStore, store


client = TestClient(app)


def setup_function():
    store.reset()


def create_board(name="Spring launch"):
    response = client.post("/boards", json={"name": name})
    assert response.status_code == 200
    return response.json()


def create_card(board_id, column_id="todo", title="Polish the home page hero"):
    response = client.post(
        f"/boards/{board_id}/cards",
        json={"columnId": column_id, "title": title},
    )
    assert response.status_code == 200
    return response.json()


def test_list_boards_returns_board_summaries():
    board = create_board()

    response = client.get("/boards")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": board["id"],
            "name": "Spring launch",
            "createdAt": board["createdAt"],
            "updatedAt": board["updatedAt"],
            "columns": board["columns"],
            "cardCount": 0,
        }
    ]
    assert "cards" not in response.json()[0]


def test_create_get_rename_and_delete_board():
    board = create_board()
    board_id = board["id"]

    fetched = client.get(f"/boards/{board_id}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "Spring launch"
    assert [column["name"] for column in fetched.json()["columns"]] == [
        "To Do",
        "In Progress",
        "Done",
    ]

    renamed = client.patch(f"/boards/{board_id}", json={"name": "Website redesign"})
    assert renamed.status_code == 200
    assert renamed.json()["name"] == "Website redesign"

    deleted = client.delete(f"/boards/{board_id}")
    assert deleted.status_code == 200
    assert deleted.json() is True
    assert client.get(f"/boards/{board_id}").status_code == 404


def test_create_card_updates_column_order_and_is_returned_in_board():
    board = create_board()
    card = create_card(board["id"])

    assert card["title"] == "Polish the home page hero"
    assert card["columnId"] == "todo"
    assert card["activityLog"][0]["type"] == "created"

    detail = client.get(f"/boards/{board['id']}").json()
    assert detail["columns"][0]["cardOrder"] == [card["id"]]
    assert detail["cards"][0]["id"] == card["id"]


def test_update_card_supports_partial_edits_and_move():
    board = create_board()
    first = create_card(board["id"], title="First task")
    second = create_card(board["id"], title="Second task")

    edited = client.patch(
        f"/cards/{first['id']}",
        json={
            "description": "Add more context.",
            "dueDate": "2026-09-18",
            "labels": [{"id": "label-design", "name": "Design", "color": "#8267d8"}],
            "assignee": {"id": "user-maya", "name": "Maya Chen", "color": "#7b61ff"},
        },
    )
    assert edited.status_code == 200
    assert edited.json()["description"] == "Add more context."
    assert edited.json()["assignee"]["name"] == "Maya Chen"
    assert edited.json()["activityLog"][0]["type"] == "edited"

    moved = client.patch(
        f"/cards/{first['id']}",
        json={"columnId": "progress", "position": 0},
    )
    assert moved.status_code == 200
    assert moved.json()["columnId"] == "progress"
    detail = client.get(f"/boards/{board['id']}").json()
    assert detail["columns"][0]["cardOrder"] == [second["id"]]
    assert detail["columns"][1]["cardOrder"] == [first["id"]]
    assert "moved from To Do to In Progress" in detail["cards"][0]["activityLog"][0]["detail"]


def test_add_comment_returns_comment_and_updated_card():
    board = create_board()
    card = create_card(board["id"])

    response = client.post(
        f"/cards/{card['id']}/comments",
        json={
            "text": "This looks ready for review.",
            "author": {"id": "user-you", "name": "Alex Morgan", "color": "#d95d39"},
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["comment"]["text"] == "This looks ready for review."
    assert body["comment"]["author"]["name"] == "Alex Morgan"
    assert body["card"]["comments"][0]["id"] == body["comment"]["id"]
    assert body["card"]["activityLog"][0]["type"] == "commented"


def test_invalid_and_missing_resources_return_contract_errors():
    invalid_board = client.post("/boards", json={"name": "   "})
    assert invalid_board.status_code == 400
    assert "message" in invalid_board.json()

    missing_board = client.get("/boards/not-a-board")
    assert missing_board.status_code == 404
    assert missing_board.json() == {"message": "Board not found"}

    missing_card = client.patch("/cards/not-a-card", json={"title": "Nope"})
    assert missing_card.status_code == 404
    assert missing_card.json() == {"message": "Card not found"}


def test_card_patch_requires_a_change_and_valid_column():
    board = create_board()
    card = create_card(board["id"])

    empty_patch = client.patch(f"/cards/{card['id']}", json={})
    assert empty_patch.status_code == 400
    assert "message" in empty_patch.json()

    invalid_move = client.patch(
        f"/cards/{card['id']}",
        json={"columnId": "not-a-column", "position": 0},
    )
    assert invalid_move.status_code == 400
    assert invalid_move.json() == {"message": "Column not found"}


def test_boards_are_persisted_in_the_database():
    board = create_board("Persisted board")

    fresh_store = DatabaseStore()

    assert fresh_store.get_board(board["id"]).name == "Persisted board"
    assert fresh_store.list_boards()[0].id == board["id"]
