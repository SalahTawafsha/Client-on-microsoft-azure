import pytest
import random
import string

from solution.models.azure_client import AzureClient
from solution.models.sync_azure_client import SyncAzureClient
from solution.telegram_bot import TelegramBot


@pytest.fixture(scope="module")
def client():
    settings = {
        "token": "wnvfg4foetsqbr5h7vbgjrvwbe4mveaxv7nv5rzfwqdfpo3wrfxq",
        "organization": "salaht321-testing",
    }
    client: SyncAzureClient = SyncAzureClient(settings, TelegramBot())
    yield client
    client.close()


@pytest.fixture(scope="module")
def random_name():
    letters = string.ascii_lowercase
    random_name = ''.join(random.choice(letters) for _ in range(8))
    return random_name


EMPTY_LEN: int = 0


def test_create_project(client, random_name):
    """ Test create azure project """
    response = client.create_project(random_name, "description")

    assert response.status_code == AzureClient.ACCEPTED_STATUS_CODE
    assert response.response["name"] == random_name


def test_delete_project(client, random_name):
    """ Test delete azure project """
    response = client.delete_project(random_name)

    assert response.status_code == AzureClient.ACCEPTED_STATUS_CODE
    assert response.response["name"] == random_name
    assert response.message == f"Project '{random_name}' deleted successfully."


def test_create_exist_project(client):
    """ Test create project with existed name project """
    response = client.create_project("salaht321", "description")

    assert response.status_code == AzureClient.PROJECT_ALREADY_EXIST_STATUS_CODE
    assert response.message == "Project 'salaht321' is already exist."


def test_delete_not_exist_project(client):
    """ Test delete project with not existed name project """
    response = client.delete_project("not exist name")

    assert response.status_code == AzureClient.NOT_FOUND_STATUS_CODE
    assert response.message == "Project 'not exist name' not found."


def test_list_projects(client):
    """ Test list azure project """
    response = client.list_projects()

    assert response.status_code == AzureClient.OK_STATUS_CODE
    assert response.message == "Projects listed successfully."
    assert len(response.response) > EMPTY_LEN


def test_get_project(client):
    """ Test get azure project """
    response = client.get_project("salaht321")

    assert response.status_code == AzureClient.OK_STATUS_CODE
    assert response.message == "Project found."
    assert response.response["name"] == "salaht321"


def test_get_not_exist_project(client):
    """ Test get azure project with not existed name project """
    response = client.get_project("not exist name")

    assert response.status_code == AzureClient.NOT_FOUND_STATUS_CODE
    assert response.message == "Project 'not exist name' not found."


@pytest.mark.parametrize("work_item_type", ["Task", "Bug", "Epic"])
def test_create_work_item(client, work_item_type,
                          random_name):  # note that no need to test exist work item because that allowed
    """ Test create work item """
    response = client.create_work_item("salaht321", work_item_type, random_name)

    assert response.status_code == AzureClient.OK_STATUS_CODE
    assert response.message == f"Work item '{random_name}' created successfully."
    assert response.response["title"] == random_name
    assert response.response["type"] == work_item_type


def test_create_work_item_with_not_exist_project(client, random_name):
    """ Test create work item with not existed name project """
    response = client.create_work_item("not exist project", "Task", random_name)

    assert response.status_code == AzureClient.NOT_FOUND_STATUS_CODE
    assert response.message == "Project 'not exist project' not found."


def test_create_work_item_with_not_exist_type(client, random_name):
    """ Test create work item with not existed type """
    response = client.create_work_item("salaht321", "not exist type", random_name)

    assert response.status_code == AzureClient.NOT_FOUND_STATUS_CODE
    assert response.message == "Work item type 'not exist type' does not exist in the project."


@pytest.mark.asyncio
def test_list_work_items(client):
    """ Test list work items """
    response = client.list_work_items("salaht321")

    assert response.status_code == AzureClient.OK_STATUS_CODE
    assert response.message == "Work items listed successfully."
    assert len(response.response) > EMPTY_LEN


# to delete two work items that created in this test and let one not deleted to use in update test
@pytest.mark.parametrize("run", range(2))
def test_delete_work_item(run, client, random_name):
    """ Test delete work item """
    response = client.delete_work_item("salaht321", random_name)

    assert response.status_code == AzureClient.OK_STATUS_CODE
    assert response.message == f"Work item '{random_name}' deleted successfully."


def test_delete_not_exist_work_item(client):
    """ Test delete work item with not existed name work item """
    response = client.delete_work_item("salaht321", "not exist name")

    assert response.status_code == AzureClient.NOT_FOUND_STATUS_CODE
    assert response.message == f"Work item 'not exist name' not found."


def test_list_work_items_not_exist_project(client):
    """ Test list work items with not existed name project """
    response = client.list_work_items("not exist project")

    assert response.status_code == AzureClient.NOT_FOUND_STATUS_CODE
    assert response.message == "Project 'not exist project' not found."


def test_get_work_item(client):
    """ Test get work item """
    response = client.get_work_item("salaht321", "exist work item")

    assert response.status_code == AzureClient.OK_STATUS_CODE
    assert response.message == "Work item found."
    assert response.response["title"] == "exist work item"


def test_get_not_exist_work_item(client):
    """ Test get work item with not existed name work item """
    response = client.get_work_item("salaht321", "not exist work item")

    assert response.status_code == AzureClient.NOT_FOUND_STATUS_CODE
    assert response.message == "Work item 'not exist work item' not found."


def test_update_work_item(client, random_name):
    """ Test update work item """
    response = client.update_work_item("salaht321", random_name, "hello")

    assert response.status_code == AzureClient.OK_STATUS_CODE
    assert response.message == f"Work item '{random_name}' updated to 'hello'."
    client.delete_work_item("salaht321", "hello")


def test_update_not_exist_work_item(client):
    """ Test update work item with not existed name work item """
    response = client.update_work_item("salaht321", "not exist work item", "hello")

    assert response.status_code == AzureClient.NOT_FOUND_STATUS_CODE
    assert response.message == "Work item 'not exist work item' not found."
