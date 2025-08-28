import pytest
from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId

from app.db.project import (
    db_get_project,
    db_add_todo,
    db_update_todo,
    db_delete_todo,
    db_get_todo_items,
    db_add_todo_status,
    db_delete_todo_status,
    db_reorder_todo_statuses,
)
from app.schemas.project import (
    AddTodoRequest,
    UpdateTodoRequest,
    AddTodoStatusRequest,
    DeleteTodoStatusRequest,
    ReorderTodoStatusesRequest,
)
from app.test_shared.constants import (
    MOCK_PROJECT_ID,
    MOCK_PROJECT_NAME,
    MOCK_PROJECT_DESCRIPTION,
    MOCK_USER_ID,
    MOCK_USER_2_ID,
    MOCK_INSERTED_ID,
)


@pytest.mark.asyncio
async def test_db_get_project_success():
    mock_db = AsyncMock()
    mock_projects_collection = AsyncMock()
    mock_projects_collection.find_one.return_value = {
        "_id": ObjectId(MOCK_PROJECT_ID),
        "name": MOCK_PROJECT_NAME,
        "description": MOCK_PROJECT_DESCRIPTION,
        "todo_statuses": [
            {"id": ObjectId(), "name": "To Do"},
            {"id": ObjectId(), "name": "Done"},
        ],
        "todo_ids": [],
    }
    mock_db.__getitem__.return_value = mock_projects_collection

    result = await db_get_project(MOCK_PROJECT_ID, mock_db)

    assert isinstance(result, dict)
    assert result["_id"] == MOCK_PROJECT_ID
    assert result["name"] == MOCK_PROJECT_NAME
    assert result["description"] == MOCK_PROJECT_DESCRIPTION
    assert isinstance(result["todo_statuses"], list)
    assert result["todo_ids"] == []


@pytest.mark.asyncio
async def test_db_add_todo_success():
    mock_db = AsyncMock()
    mock_todos_collection = AsyncMock()
    mock_projects_collection = AsyncMock()
    mock_result = AsyncMock()
    mock_result.inserted_id = ObjectId(MOCK_INSERTED_ID)
    mock_todos_collection.insert_one.return_value = mock_result
    mock_projects_collection.update_one.return_value = None

    def getitem(name):
        if name == "todos":
            return mock_todos_collection
        return mock_projects_collection

    mock_db.__getitem__.side_effect = getitem
    todo_req = AddTodoRequest(
        name="Todo",
        description="Desc",
        status_id=MOCK_USER_ID,
        owner_id=MOCK_USER_2_ID,
    )

    result = await db_add_todo(MOCK_PROJECT_ID, todo_req, mock_db)

    assert result is None
    mock_todos_collection.insert_one.assert_called_once()
    mock_projects_collection.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_db_update_todo_success():
    mock_db = AsyncMock()
    mock_todos_collection = AsyncMock()
    mock_db.__getitem__.return_value = mock_todos_collection
    update_req = UpdateTodoRequest(
        todo_id=MOCK_INSERTED_ID,
        name="Updated",
        description="Desc",
        status_id=MOCK_USER_ID,
        owner_id=MOCK_USER_2_ID,
    )

    result = await db_update_todo(MOCK_PROJECT_ID, update_req, mock_db)

    assert result is None
    mock_todos_collection.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_db_delete_todo_success():
    mock_db = AsyncMock()
    mock_todos_collection = AsyncMock()
    mock_projects_collection = AsyncMock()
    mock_todos_collection.delete_one.return_value = None
    mock_projects_collection.update_one.return_value = None

    def getitem(name):
        if name == "todos":
            return mock_todos_collection
        return mock_projects_collection

    mock_db.__getitem__.side_effect = getitem
    todo_id = MOCK_INSERTED_ID

    result = await db_delete_todo(MOCK_PROJECT_ID, todo_id, mock_db)

    assert result is None
    mock_todos_collection.delete_one.assert_called_once()
    mock_projects_collection.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_db_get_todo_items_success():
    mock_db = AsyncMock()
    mock_projects_collection = AsyncMock()
    mock_projects_collection.find_one.return_value = {
        "_id": ObjectId(MOCK_PROJECT_ID),
        "todo_ids": [ObjectId(MOCK_INSERTED_ID)],
    }
    mock_todos_collection = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock(
        return_value=[
            {
                "_id": ObjectId(MOCK_INSERTED_ID),
                "name": "Todo",
                "description": "Desc",
                "status_id": ObjectId(MOCK_USER_ID),
                "owner_id": ObjectId(MOCK_USER_2_ID),
            }
        ]
    )
    mock_todos_collection.find.return_value = mock_cursor

    def getitem(name):
        if name == "projects":
            return mock_projects_collection
        return mock_todos_collection

    mock_db.__getitem__.side_effect = getitem

    result = await db_get_todo_items(MOCK_PROJECT_ID, mock_db)

    assert isinstance(result, list)
    assert result[0]["_id"] == MOCK_INSERTED_ID
    assert result[0]["name"] == "Todo"
    assert result[0]["description"] == "Desc"
    assert result[0]["status_id"] == MOCK_USER_ID
    assert result[0]["owner_id"] == MOCK_USER_2_ID


@pytest.mark.asyncio
async def test_db_add_todo_status_success():
    mock_db = AsyncMock()
    mock_projects_collection = AsyncMock()
    mock_projects_collection.update_one.return_value = None
    mock_db.__getitem__.return_value = mock_projects_collection
    status_req = AddTodoStatusRequest(name="In Progress")

    result = await db_add_todo_status(MOCK_PROJECT_ID, status_req.name, mock_db)

    assert result is None
    mock_projects_collection.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_db_delete_todo_status_success():
    mock_db = AsyncMock()
    mock_projects_collection = AsyncMock()
    mock_projects_collection.update_one.return_value = None
    mock_db.__getitem__.return_value = mock_projects_collection
    status_req = DeleteTodoStatusRequest(status_id=MOCK_INSERTED_ID)

    result = await db_delete_todo_status(MOCK_PROJECT_ID, status_req.status_id, mock_db)

    assert result is None
    mock_projects_collection.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_db_reorder_todo_statuses_success():
    mock_db = AsyncMock()
    mock_projects_collection = AsyncMock()
    mock_projects_collection.update_one.return_value = None
    mock_db.__getitem__.return_value = mock_projects_collection
    new_statuses = [
        {"id": MOCK_INSERTED_ID, "name": "To Do"},
        {"id": MOCK_USER_ID, "name": "Done"},
    ]

    result = await db_reorder_todo_statuses(MOCK_PROJECT_ID, new_statuses, mock_db)

    assert result is None
    mock_projects_collection.update_one.assert_called_once()
