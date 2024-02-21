"""Main module for the solution that has command line
 interface for the user to interact with the Azure organization. """
import asyncio
from solution.models.data_classes.data_classes import Success
from solution.models.sync_azure_client import SyncAzureClient
from solution.models.async_azure_client import AsyncAzureClient
from typing import Union

from solution.telegram_bot import TelegramBot


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


def work_item_operations(client: Union[AsyncAzureClient, SyncAzureClient],
                         project_name: str, selected_project_id: str, project_choice: str):
    """ List all work item operations for async client. """
    match project_choice:
        case "1":
            work_item_title = input("Enter new work item title: ").strip()
            work_item_type = input("Enter new work item type: ").strip()
            return client.create_work_item(selected_project_id,
                                           work_item_type, work_item_title)

        case "2":
            return client.list_work_items(project_name)

        case "3":
            work_item_title = input("Enter work item title to update title: ").strip()
            new_work_item_title = input("Enter new work item title: ").strip()
            return client.update_work_item(project_name, work_item_title, new_work_item_title)

        case "4":
            work_item_title = input("Enter work item title to delete: ").strip()
            return client.delete_work_item(project_name, work_item_title)

        case "5":
            work_item_title = input("Enter work item title to get it's info: ").strip()
            return client.get_work_item(project_name, work_item_title)

        case "6":
            return

        case _:
            print("Invalid choice. Please try again.")


def get_request(choice, client):
    match choice:
        case "1":
            name = input("Enter Project Name: ").strip()
            description = input("Enter Project Description: ").strip()

            return client.create_project(name, description)
        case "2":
            return client.list_projects()

        case "3":
            project_name = input("Enter Project Name to delete it: ").strip()
            return client.delete_project(project_name)

        case "4":
            project_name = input("Enter Project Name: ").strip()
            return client.get_project(project_name)

        case "5":
            return client.close()
        case _:
            print("Invalid choice. Please try again.")


def handle_work_item_response(work_item_response, project_choice):
    match project_choice:
        case "1":
            print(work_item_response.message)

        case "2":
            if isinstance(work_item_response, Success):
                if len(work_item_response.response) == 0:
                    print("No work items found.")
                    return

                print("---------------------------------------------")
                print("\t%-15s: %s" % ("Work Item Type", "Work Item Title"))
                print("---------------------------------------------")
                for work_item in work_item_response.response.values():
                    print("\t%-15s: %-30s" % (
                        work_item["type"], work_item["title"]))
            else:
                print(work_item_response.message)
        case "3":
            print(work_item_response.message)

        case "4":
            print(work_item_response.message)

        case "5":
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


def handle_response(response, choice):
    match choice:
        case "1":
            print(response.message)

        case "2":
            if isinstance(response, Success):
                if len(response.response) == 0:
                    print("No projects found.")
                    return

                print("Projects Names:")
                for key, value in response.response.items():
                    print(f'\t{key}. {value}')
            else:
                print(response.message)

        case "3":
            print(response.message)

        case "4":
            if isinstance(response, Success):
                return response.response["id"], response.response["name"]

            else:
                print(response.message)


async def pick_async():
    client = AsyncAzureClient(telegram_bot=TelegramBot())
    while True:
        print_project_choices()
        choice = input("Enter your choice: ").strip()

        if choice.isnumeric() and 0 < int(choice) < 5:
            response = await get_request(choice, client)

            if choice != "4":
                handle_response(response, choice)
            else:
                project_id, project_name = handle_response(response, choice)

                while True:
                    print_work_item_choices(project_name)
                    project_choice = input("Enter your choice: ").strip()

                    if project_choice.isnumeric() and 0 < int(project_choice) < 6:
                        response = await work_item_operations(client, project_name, project_id, project_choice)
                    elif project_choice == "6":
                        break
                    else:
                        print("Invalid choice. Please try again.")

                    handle_work_item_response(response, project_choice)

        elif choice == "5":
            break
        else:
            print("Invalid choice. Please try again.")


def pick_sync():
    client = SyncAzureClient(telegram_bot=TelegramBot())
    while True:
        print_project_choices()
        choice = input("Enter your choice: ").strip()

        if choice.isnumeric() and 0 < int(choice) < 5:
            response = get_request(choice, client)

            if choice != "4":
                handle_response(response, choice)
            else:
                project_id, project_name = handle_response(response, choice)

                while True:
                    print_work_item_choices(project_name)
                    project_choice = input("Enter your choice: ").strip()

                    if project_choice.isnumeric() and 0 < int(project_choice) < 6:
                        response = work_item_operations(client, project_name, project_id, project_choice)
                    elif project_choice == "6":
                        break
                    else:
                        print("Invalid choice. Please try again.")

                    handle_work_item_response(response, project_choice)

        elif choice == "5":
            break
        else:
            print("Invalid choice. Please try again.")


def project_operations(is_async: bool = False):
    if is_async:
        asyncio.run(pick_async())
    else:
        pick_sync()


if __name__ == "__main__":
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
            project_operations(False)
        elif client_type == "2":
            project_operations(True)
        else:
            print("Thank you for using Azure API!")
            break
