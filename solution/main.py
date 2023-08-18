"""Main module for the solution that has command line
 interface for the user to interact with the Azure organization. """
import asyncio
import json
from solution.data_classes.data_classes import Success
from solution.solution.sync_azure_client import SyncAzureClient
from solution.solution.async_azure_client import AsyncAzureClient


def print_project_choices():
    """Print all project operations."""
    print("*******************************************")
    print("What would you like to do?")
    print("1. Create a new Project.")
    print("2. List all Projects.")
    print("3. Delete a Project.")
    print("4. Get Project.")
    print("5. Exit.")


def print_work_item_choices(project_name: str):
    """Print all work item operations."""
    print(f"what would you like to do with the project '{project_name}'?")
    print("1. Create new work item.")
    print("2. List all work items.")
    print("3. Update a work item.")
    print("4. Delete a work item.")
    print("5. Get work item.")
    print("6. Return to main menu.")


def sync_work_item_operations(client: SyncAzureClient, project_name: str, selected_project_id: str):
    """List all work item operations for sync client."""
    while True:
        print_work_item_choices(project_name)
        project_choice = input("Enter your choice: ").strip()
        match project_choice:
            case "1":
                work_item_title = input("Enter new work item title: ").strip()
                work_item_type = input("Enter new work item type: ").strip()
                work_item_response = client.create_work_item(selected_project_id,
                                                             work_item_type, work_item_title)

                print(work_item_response.message)
            case "2":
                work_item_response = client.list_work_items(project_name)

                if isinstance(work_item_response, Success):
                    if len(work_item_response.response) == 0:
                        print("No work items found.")
                        continue

                    print("---------------------------------------------")
                    print("\t%-15s: %s" % ("Work Item Type", "Work Item Title"))
                    print("---------------------------------------------")
                    for work_item in work_item_response.response.values():
                        print("\t%-15s: %-30s" % (
                            work_item["type"], work_item["title"]))
                else:
                    print(work_item_response.message)
            case "3":
                work_item_title = input("Enter work item title to update title: ").strip()
                get_work_item_response = client.get_work_item(project_name, work_item_title)

                if get_work_item_response.message != "Work item found.":
                    print(get_work_item_response.message)
                    continue

                new_work_item_title = input("Enter new work item title: ").strip()
                work_item_response = client.update_work_item(project_name,
                                                             work_item_title, new_work_item_title)
                print(work_item_response.message)
            case "4":
                work_item_title = input("Enter work item title to delete: ").strip()
                work_item_response = client.delete_work_item(project_name, work_item_title)

                print(work_item_response.message)
            case "5":
                work_item_title = input("Enter work item title to get it's info: ").strip()
                work_item_response = client.get_work_item(project_name, work_item_title)

                if isinstance(work_item_response, Success):
                    result = work_item_response.response
                    print(f"Work item '{result['title']}' details:")
                    print(f"\tid: {result['id']}")
                    print(f"\ttype: {result['type']}")
                    print(f"\tstate: {result['state']}")
                else:
                    print(work_item_response.message)

            case "6":
                return
            case _:
                print("Invalid choice. Please try again.")
        print("------------------------------------------------------------")


def sync_list():
    """List all project operations for sync client."""

    try:
        client = SyncAzureClient()
    except json.decoder.JSONDecodeError:
        print("Error occurred while reading settings.init file.")
        print("it's must be in json format.")
        return

    while True:
        print_project_choices()
        choice = input("Enter your choice: ").strip()

        match choice:
            case "1":
                name = input("Enter Project Name: ").strip()
                get_project_response = client.get_project(name)

                if get_project_response.message == "Project found.":
                    print("Project already exists.")
                    continue

                description = input("Enter Project Description: ").strip()
                response = client.create_project(name, description)

                print(response.message)

            case "2":
                response = client.list_projects()

                if isinstance(response, Success):
                    if len(response.response) == 0:
                        print("No projects found.")
                        continue

                    print("Projects Names:")
                    for key, value in response.response.items():
                        print(f'\t{key}. {value}')
                else:
                    print(response.message)

            case "3":
                project_name = input("Enter Project Name to delete it: ").strip()
                response = client.delete_project(project_name)
                print(response.message)

            case "4":
                project_name = input("Enter Project Name: ").strip()
                response = client.get_project(project_name)

                if isinstance(response, Success):
                    project_id = response.response["id"]

                    sync_work_item_operations(client, project_name, project_id)

                else:
                    print(response.message)
            case "5":
                client.close()
                break
            case _:
                print("Invalid choice. Please try again.")


async def async_work_item_operations(client: AsyncAzureClient,
                                     project_name: str, selected_project_id: str):
    """ List all work item operations for async client. """
    while True:
        print_work_item_choices(project_name)
        project_choice = input("Enter your choice: ").strip()
        match project_choice:
            case "1":
                work_item_title = input("Enter new work item title: ").strip()
                work_item_type = input("Enter new work item type: ").strip()
                work_item_response = await client.create_work_item(selected_project_id,
                                                                   work_item_type, work_item_title)

                print(work_item_response.message)
            case "2":
                work_item_response = await client.list_work_items(project_name)

                if isinstance(work_item_response, Success):
                    if len(work_item_response.response) == 0:
                        print("No work items found.")
                        continue

                    print("---------------------------------------------")
                    print("\t%-15s: %s" % ("Work Item Type", "Work Item Title"))
                    print("---------------------------------------------")
                    for work_item in work_item_response.response.values():
                        print("\t%-15s: %-30s" % (
                            work_item["type"], work_item["title"]))
                else:
                    print(work_item_response.message)
            case "3":
                work_item_title = input("Enter work item title to update title: ").strip()
                get_work_item_response = await client.get_work_item(project_name, work_item_title)

                if get_work_item_response.message != "Work item found.":
                    print(get_work_item_response.message)
                    continue

                new_work_item_title = input("Enter new work item title: ").strip()
                work_item_response = await client.update_work_item(project_name, work_item_title,
                                                                   new_work_item_title)
                print(work_item_response.message)

            case "4":
                work_item_title = input("Enter work item title to delete: ").strip()
                work_item_response = await client.delete_work_item(project_name, work_item_title)

                print(work_item_response.message)
            case "5":
                work_item_title = input("Enter work item title to get it's info: ").strip()
                work_item_response = await client.get_work_item(project_name, work_item_title)

                if isinstance(work_item_response, Success):
                    result = work_item_response.response
                    print(f"Work item '{result['title']}' details:")
                    print(f"\tid: {result['id']}")
                    print(f"\ttype: {result['type']}")
                    print(f"\tstate: {result['state']}")
                else:
                    print(work_item_response.message)

            case "6":
                return
            case _:
                print("Invalid choice. Please try again.")
        print("------------------------------------------------------------")


async def async_list():
    """List all project operations for async client."""
    try:
        client = AsyncAzureClient()
    except json.decoder.JSONDecodeError:
        print("Error occurred while reading settings.init file.")
        print("it's must be in json format.")
        return

    while True:
        print_project_choices()
        choice = input("Enter your choice: ").strip()

        match choice:
            case "1":
                name = input("Enter Project Name: ").strip()
                get_response = await client.get_project(name)
                if get_response.message == "Project found.":
                    print("Project already exists.")
                    continue

                description = input("Enter Project Description: ").strip()
                response = await client.create_project(name, description)

                print(response.message)

            case "2":
                response = await client.list_projects()

                if isinstance(response, Success):
                    if len(response.response) == 0:
                        print("No projects found.")
                        continue

                    print("Projects Names:")
                    for key, value in response.response.items():
                        print(f'\t{key}. {value}')
                else:
                    print(response.message)

            case "3":
                project_name = input("Enter Project Name to delete it: ").strip()
                response = await client.delete_project(project_name)
                print(response.message)

            case "4":
                project_name = input("Enter Project Name: ").strip()
                response = await client.get_project(project_name)

                if isinstance(response, Success):
                    project_id = response.response["id"]

                    await async_work_item_operations(client, project_name, project_id)

                else:
                    print(response.message)
            case "5":
                await client.close()
                break
            case _:
                print("Invalid choice. Please try again.")


if __name__ == '__main__':
    print("Welcome to Azure API!")
    while True:
        print("*******************************************")
        print("How would you like to run?")
        print("1. Sync client.")
        print("2. Async client.")
        print("3. Exit.")
        client_type = input("Enter your choice: ").strip()

        while client_type not in ["1", "2", "3"]:
            print("Invalid choice. Please choose 1, 2 or 3.")
            client_type = input("Enter your choice: ").strip()

        if client_type == "1":
            sync_list()
        elif client_type == "2":
            asyncio.run(async_list())
        else:
            print("Thank you for using Azure API!")
            break
