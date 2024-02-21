import asyncio

import pytest
import random
import string

from solution.models.async_azure_client import AsyncAzureClient
from solution.models.azure_client import AzureClient
from solution.telegram_bot import TelegramBot


@pytest.fixture(scope="module")
def random_name():
    letters = string.ascii_lowercase
    random_name = ''.join(random.choice(letters) for _ in range(8))
    return random_name


EMPTY_LEN: int = 0


@pytest.fixture(scope="module")
def get_client():
    settings = {
        "token": "xem42qtnkiobxaxookczdlr3ps65hxdgyxbr7bjgwyfccrulb6rq",
        "organization": "salaht321-testing",
    }
    client = AsyncAzureClient(settings, TelegramBot())
    return client


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
async def test_create_project(random_name, get_client):
    """ Test create azure project """
    response = await get_client.create_project(random_name, "description")

    assert response.status_code == AzureClient.ACCEPTED_STATUS_CODE
    assert response.response["name"] == random_name


@pytest.mark.asyncio
async def test_delete_project(random_name, get_client):
    """ Test delete azure project """
    response = await get_client.delete_project(random_name)

    assert response.status_code == AzureClient.ACCEPTED_STATUS_CODE
    assert response.response["name"] == random_name
    assert response.message == f"Project '{random_name}' deleted successfully."


@pytest.mark.asyncio
async def test_create_exist_project(get_client):
    """ Test create project with existed name project """
    response = await get_client.create_project("salaht321", "description")

    assert response.status_code == AzureClient.PROJECT_ALREADY_EXIST_STATUS_CODE
    assert response.message == "Project 'salaht321' is already exist."


@pytest.mark.asyncio
async def test_delete_not_exist_project(get_client):
    """ Test delete project with not existed name project """
    response = await get_client.delete_project("not exist name")

    assert response.status_code == AzureClient.NOT_FOUND_STATUS_CODE
    assert response.message == "Project 'not exist name' not found."


@pytest.mark.asyncio
async def test_list_projects(get_client):
    """ Test list azure project """
    response = await get_client.list_projects()

    assert response.status_code == AzureClient.OK_STATUS_CODE
    assert response.message == "Projects listed successfully."
    assert len(response.response) > EMPTY_LEN


@pytest.mark.asyncio
async def test_get_project(get_client):
    """ Test get azure project """
    response = await get_client.get_project("salaht321")

    assert response.status_code == AzureClient.OK_STATUS_CODE
    assert response.message == "Project found."
    assert response.response["name"] == "salaht321"


@pytest.mark.asyncio
async def test_get_not_exist_project(get_client):
    """ Test get azure project with not existed name project """
    response = await get_client.get_project("not exist name")

    assert response.status_code == AzureClient.NOT_FOUND_STATUS_CODE
    assert response.message == "Project 'not exist name' not found."


@pytest.mark.asyncio
@pytest.mark.parametrize("work_item_type", ["Task", "Bug", "Epic"])
async def test_create_work_item(random_name, get_client,
                                work_item_type):  # note that no need to test exist work item because that allowed
    """ Test create work item """
    response = await get_client.create_work_item("salaht321", work_item_type, random_name)

    assert response.status_code == AzureClient.OK_STATUS_CODE
    assert response.message == f"Work item '{random_name}' created successfully."
    assert response.response["title"] == random_name
    assert response.response["type"] == work_item_type


@pytest.mark.asyncio
async def test_create_work_item_with_not_exist_project(random_name, get_client):
    """ Test create work item with not existed name project """
    response = await get_client.create_work_item("not exist project", "Task", random_name)

    assert response.status_code == AzureClient.NOT_FOUND_STATUS_CODE
    assert response.message == "Project 'not exist project' not found."


@pytest.mark.asyncio
async def test_create_work_item_with_not_exist_type(random_name, get_client):
    """ Test create work item with not existed type """
    response = await get_client.create_work_item("salaht321", "not exist type", random_name)

    assert response.status_code == AzureClient.NOT_FOUND_STATUS_CODE
    assert response.message == "Work item type 'not exist type' does not exist in the project."


@pytest.mark.asyncio
# to delete two work items that created in this test and let one not deleted to use in update test
@pytest.mark.parametrize("run", range(2))
async def test_delete_work_item(random_name, get_client, run):
    """ Test delete work item """
    response = await get_client.delete_work_item("salaht321", random_name)

    assert response.status_code == AzureClient.OK_STATUS_CODE
    assert response.message == f"Work item '{random_name}' deleted successfully."


@pytest.mark.asyncio
async def test_delete_not_exist_work_item(get_client):
    """ Test delete work item with not existed name work item """
    response = await get_client.delete_work_item("salaht321", "not exist name")

    assert response.status_code == AzureClient.NOT_FOUND_STATUS_CODE
    assert response.message == f"Work item 'not exist name' not found."


@pytest.mark.asyncio
async def test_list_work_items(get_client):
    """ Test list work items """
    response = await get_client.list_work_items("salaht321")

    assert response.status_code == AzureClient.OK_STATUS_CODE
    assert response.message == "Work items listed successfully."
    assert len(response.response) > EMPTY_LEN


@pytest.mark.asyncio
async def test_list_work_items_not_exist_project(get_client):
    """ Test list work items with not existed name project """
    response = await get_client.list_work_items("not exist project")

    assert response.status_code == AzureClient.NOT_FOUND_STATUS_CODE
    assert response.message == "Project 'not exist project' not found."


@pytest.mark.asyncio
async def test_get_work_item(get_client):
    """ Test get work item """
    response = await get_client.get_work_item("salaht321", "exist work item")

    assert response.status_code == AzureClient.OK_STATUS_CODE
    assert response.message == "Work item found."
    assert response.response["title"] == "exist work item"


@pytest.mark.asyncio
async def test_get_not_exist_work_item(get_client):
    """ Test get work item with not existed name work item """
    response = await get_client.get_work_item("salaht321", "not exist work item")

    assert response.status_code == AzureClient.NOT_FOUND_STATUS_CODE
    assert response.message == "Work item 'not exist work item' not found."


@pytest.mark.asyncio
async def test_update_work_item(random_name, get_client):
    """ Test update work item """
    response = await get_client.update_work_item("salaht321", random_name, "hello")

    assert response.status_code == AzureClient.OK_STATUS_CODE
    assert response.message == f"Work item '{random_name}' updated to 'hello'."
    await get_client.delete_work_item("salaht321", "hello")


@pytest.mark.asyncio
async def test_update_not_exist_work_item(get_client):
    """ Test update work item with not existed name work item """
    response = await get_client.update_work_item("salaht321", "not exist work item", "hello")

    assert response.status_code == AzureClient.NOT_FOUND_STATUS_CODE
    assert response.message == "Work item 'not exist work item' not found."
