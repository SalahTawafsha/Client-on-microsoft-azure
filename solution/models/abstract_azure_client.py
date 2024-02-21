import os
from abc import ABC, abstractmethod

from solution.models.data_classes.data_classes import Success, Error, AzureSettings
from solution.telegram_bot import TelegramBot

from configparser import ConfigParser


class AzureClient(ABC):
    OK_STATUS_CODE = 200
    ACCEPTED_STATUS_CODE = 202
    NON_AUTHORIZED_STATUS_CODES = [203, 401]
    PROJECT_ALREADY_EXIST_STATUS_CODE = 400
    NON_AUTHORIZED_STATUS_CODE = 401
    NOT_FOUND_STATUS_CODE = 404

    END_POINTS = {
        "create_project": "/_apis/projects?api-version=7.0",
        "list_projects": "/_apis/projects?api-version=7.0",
        "delete_project": "/_apis/projects/{project_id}?api-version=7.0",
        "get_project": "/_apis/projects/{project_name}?api-version=7.0",
        "create_work_item": "/{project_id}/_apis/wit/workitems/${work_item_type}?api-version=7.0",
        "list_work_items": "/{project_name}/_apis/wit/wiql?api-version=7.0",
        "update_work_item": "/{project_name}/_apis/wit/workitems/{work_item_id}?api-version=7.0",
        "delete_work_item": "/{project_name}/_apis/wit/workitems/{work_item_id}?api-version=7.0",
        "get_work_item": "/{project_name}/_apis/wit/workitems/{work_item_id}?api-version=7.0"
    }

    def __init__(self, settings: dict = None, telegram_bot: TelegramBot = None):
        if settings is None:
            settings = {}
        else:
            if not isinstance(settings, dict):
                raise TypeError("Settings must be dictionary.")

        config = ConfigParser()
        config.read(os.path.dirname(__file__) + "\\..\\settings.init")

        if "DEFAULT" in config and "token" in config["DEFAULT"] and "organization" in config["DEFAULT"]:
            self.settings = AzureSettings(config["DEFAULT"]["token"], config["DEFAULT"]["organization"])

        if settings.get("token"):
            self.settings.token = settings["token"]
        if settings.get("organization"):
            self.settings.organization = settings["organization"]

        if not self.settings.token or not self.settings.organization:
            raise ValueError("Token and organization must be specified.")

        self.telegram_bot = telegram_bot

        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        # define headers for json patch that used in create and update work item
        self._json_patch_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json-patch+json",
        }

    @abstractmethod
    def create_project(self, name: str, description: str):
        pass

    @abstractmethod
    def list_projects(self) -> Success | Error:
        pass

    @abstractmethod
    def delete_project(self, project_name: str):
        pass

    @abstractmethod
    def get_project(self, project_name: str):
        pass

    @abstractmethod
    def create_work_item(self, project_id: str, work_item_type: str, work_item_value: str):
        pass

    @abstractmethod
    def list_work_items(self, project_name: str):
        pass

    @abstractmethod
    def update_work_item(self, project_name: str, work_item_title: str, new_work_item_title: str):
        pass

    @abstractmethod
    def delete_work_item(self, project_name: str, work_item_title: str):
        pass

    @abstractmethod
    def get_work_item(self, project_name: str, work_item_title: str):
        pass

    @abstractmethod
    def close(self):
        pass

    def handle_create_project_response(self, response, name: str):
        if response.status_code == AzureClient.ACCEPTED_STATUS_CODE:
            json_response = response.json()

            response = {
                "id": json_response["id"],
                "name": name,
                "message": f"Project '{name}' created successfully."
            }

            if self.telegram_bot:
                self.telegram_bot.send_message(f"New project '{name}' created on your Azure organization "
                                               f"'{self.settings.organization}'.")

            return Success(message=f"Project '{name}' created successfully.", response=response,
                           status_code=AzureClient.ACCEPTED_STATUS_CODE)
        if response.status_code in AzureClient.NON_AUTHORIZED_STATUS_CODES:
            return Error(message="you have authorization problem, recheck your token.",
                         status_code=response.status_code)
        if response.status_code == AzureClient.PROJECT_ALREADY_EXIST_STATUS_CODE:
            return Error(message=f"Project '{name}' is already exist.",
                         status_code=response.status_code)

        return Error(message=f"Error occurred with code {response.status_code}.",
                     status_code=response.status_code)

    @classmethod
    def handle_list_projects_response(cls, get_response):
        if get_response.status_code == AzureClient.OK_STATUS_CODE:
            json_response = get_response.json()
            if json_response["count"] != 0:
                result_response = {}
                for i, response in enumerate(json_response["value"], start=1):
                    result_response.update({i: response["name"]})

                return Success(message="Projects listed successfully.", response=result_response,
                               status_code=get_response.status_code)

            return Success(message="There is no project in your organization.", response={"message": "empty"},
                           status_code=get_response.status_code)
        if get_response.status_code in AzureClient.NON_AUTHORIZED_STATUS_CODES:
            return Error(message="you have authorization problem, recheck your token.",
                         status_code=get_response.status_code)

        return Error(message=f"Error occurred with code {get_response.status_code}.",
                     status_code=get_response.status_code)

    def handle_delete_project_response(self, response, project_name):
        if response.status_code == AzureClient.ACCEPTED_STATUS_CODE:
            if self.telegram_bot:
                self.telegram_bot.send_message(
                    f"Project '{project_name}' deleted from your Azure organization "
                    f"'{self.settings.organization}'.")
            return Success(message=f"Project '{project_name}' deleted successfully.",
                           response={"message": f"Project '{project_name}' deleted successfully.",
                                     "name": project_name},
                           status_code=AzureClient.ACCEPTED_STATUS_CODE)
        if response.status_code in AzureClient.NON_AUTHORIZED_STATUS_CODES:
            return Error(message="you have authorization problem, recheck your token.",
                         status_code=response.status_code)

        return Error(message=f"Error occurred with code {response.status_code}."
                             f"", status_code=response.status_code)

    @classmethod
    def handle_get_project_response(cls, response, project_name):
        if response.status_code == AzureClient.OK_STATUS_CODE:
            json_response = response.json()
            return Success("Project found.", {"id": json_response["id"],
                                              "name": json_response["name"],
                                              "url": json_response["url"]},
                           status_code=AzureClient.OK_STATUS_CODE)
        if response.status_code in AzureClient.NON_AUTHORIZED_STATUS_CODES:
            return Error(message="you have authorization problem, recheck your token.",
                         status_code=response.status_code)
        if response.status_code == AzureClient.NOT_FOUND_STATUS_CODE:
            return Error(message=f"Project '{project_name}' not found.",
                         status_code=AzureClient.NOT_FOUND_STATUS_CODE)

        return Error(f"Error occurred with code {response.status_code}.",
                     status_code=response.status_code)

    def handle_create_work_item_response(self, response, project_id, work_item_type, work_item_value):
        if response.status_code == AzureClient.OK_STATUS_CODE:
            json_response = response.json()
            result_response = {"title": json_response["fields"]["System.Title"],
                               "id": json_response["id"],
                               "type": json_response["fields"]["System.WorkItemType"]}

            if self.telegram_bot:
                self.telegram_bot.send_message(
                    f"Work item '{work_item_value}' created on your Azure organization "
                    f"'{self.settings.organization}'.")

            return Success(message=f"Work item '{work_item_value}' created successfully.",
                           response=result_response,
                           status_code=AzureClient.OK_STATUS_CODE)
        if response.status_code in AzureClient.NON_AUTHORIZED_STATUS_CODES:
            return Error(message="you have authorization problem, recheck your token.",
                         status_code=response.status_code)
        if response.status_code == AzureClient.NOT_FOUND_STATUS_CODE:
            if f"Work item type {work_item_type} does not exist in project" \
                    in response.json()["message"]:
                return Error(message=f"Work item type '{work_item_type}' "
                                     f"does not exist in the project.",
                             status_code=AzureClient.NOT_FOUND_STATUS_CODE)

            return Error(message=f"Project '{project_id}' not found.",
                         status_code=AzureClient.NOT_FOUND_STATUS_CODE)

        return Error(message=f"Error occurred with code {response.status_code}.",
                     status_code=response.status_code)

    @classmethod
    def handle_falied_list_work_items_response(cls, response, project_name):
        if response.status_code in AzureClient.NON_AUTHORIZED_STATUS_CODES:
            return Error(message="you have authorization problem, recheck your token.",
                         status_code=response.status_code)
        if response.status_code == AzureClient.NOT_FOUND_STATUS_CODE:
            return Error(message=f"Project '{project_name}' not found.",
                         status_code=AzureClient.NOT_FOUND_STATUS_CODE)

        return Error(message=f"Error occurred with code {response.status_code}.",
                     status_code=response.status_code)

    def handle_update_work_item_response(self, response, work_item_title, new_work_item_title):
        if response.status_code == AzureClient.OK_STATUS_CODE:
            if self.telegram_bot:
                self.telegram_bot.send_message(
                    f"Work item '{work_item_title}' updated to '{new_work_item_title}'"
                    f" in your Azure organization '{self.settings.organization}'.")
            return Success(message=f"Work item '{work_item_title}' updated to '{new_work_item_title}'.",
                           response={"message": f"Work item '{work_item_title}' updated to '{new_work_item_title}'."},
                           status_code=AzureClient.OK_STATUS_CODE)

        return Error(message=f"Error occurred with code {response.status_code}.",
                     status_code=response.status_code)

    def handle_delete_work_item_response(self, response, project_name, work_item_title):
        if response.status_code == AzureClient.OK_STATUS_CODE:

            if self.telegram_bot:
                self.telegram_bot.send_message(
                    f"Work item '{work_item_title}' deleted from your Azure organization "
                    f"'{self.settings.organization}'.")

            return Success(message=f"Work item '{work_item_title}' deleted successfully.",
                           response={"message": f"Work item '{work_item_title}' deleted successfully."},
                           status_code=AzureClient.OK_STATUS_CODE)
        if response.status_code in AzureClient.NON_AUTHORIZED_STATUS_CODES:
            return Error(message="you have authorization problem, recheck your token.",
                         status_code=response.status_code)
        if response.status_code == AzureClient.NOT_FOUND_STATUS_CODE:
            return Error(message=f"Project '{project_name}' not found.",
                         status_code=AzureClient.NOT_FOUND_STATUS_CODE)

        return Error(message=f"Error occurred with code {response.status_code}.",
                     status_code=response.status_code)

    @classmethod
    def handle_get_work_item_response(cls, response):
        if response.status_code == AzureClient.OK_STATUS_CODE:
            result = response.json()

            result_response = {
                "title": result["fields"]["System.Title"],
                "id": result["id"],
                "type": result["fields"]["System.WorkItemType"],
                "state": result["fields"]["System.State"]
            }

            return Success("Work item found.", result_response, AzureClient.OK_STATUS_CODE)

        return Error(f"Error occurred with code {response.status_code}.", response.status_code)

    @classmethod
    def create_project_data(cls, name, description):
        return {"name": name,
                "description": description,
                "visibility": "private",
                "capabilities": {"versioncontrol": {"sourceControlType": "Git"},
                                 "processTemplate":
                                     {"templateTypeId": "6b724908-ef14-45cf-84f8-768b5384da45"}},
                "processTemplate": {"templateTypeId": "6b724908-ef14-45cf-84f8-768b5384da45"}}

    @classmethod
    def check_get_project_response(cls, project, project_name):
        if project.message == f"Project '{project_name}' not found.":
            return Error(message=f"Project '{project_name}' not found.",
                         status_code=AzureClient.NOT_FOUND_STATUS_CODE)
        if project.message == "you have authorization problem, recheck your token.":
            return Error(message="you have authorization problem, recheck your token.",
                         status_code=AzureClient.NON_AUTHORIZED_STATUS_CODE)

        if project.message.startswith("Error occurred with code"):
            return Error(message=project.message,
                         status_code=project.status_code)

        return project.response["id"]

    @classmethod
    def create_work_item_data(cls, work_item_value):
        return [
            {
                "op": "add",
                "path": "/fields/System.Title",
                "from": None,
                "value": work_item_value
            }
        ]

    @classmethod
    def list_work_items_body(cls, project_name):
        return {
            "query": f"Select * From WorkItems where [System.TeamProject] = '{project_name}'"
        }

    @classmethod
    def update_work_item_body(cls, work_item, work_item_title, new_work_item_title):
        if work_item == "not found.":
            return Error(message=f"Work item '{work_item_title}' not found.",
                         status_code=AzureClient.NOT_FOUND_STATUS_CODE)

        if work_item == "you have authorization problem, recheck your token.":
            return Error(message="you have authorization problem, recheck your token.",
                         status_code=AzureClient.NON_AUTHORIZED_STATUS_CODE)

        return [
            {
                "op": "replace",
                "path": "/fields/System.Title",
                "from": None,
                "value": new_work_item_title
            }
        ]

    @classmethod
    def delete_work_item_body(cls, work_item_id, work_item_title):
        if work_item_id == "not found.":
            return Error(message=f"Work item '{work_item_title}' not found.",
                         status_code=AzureClient.NOT_FOUND_STATUS_CODE)
        if work_item_id == "you have authorization problem, recheck your token.":
            return Error(message="you have authorization problem, recheck your token.",
                         status_code=AzureClient.NON_AUTHORIZED_STATUS_CODE)
