""" sync azure client module. """
import json
from base64 import b64encode
import telebot
from httpx import Client
from solution.data_classes.data_classes import Success, Error, Settings


class SyncAzureClient:
    """ Sync Azure Client class. """

    def __init__(self, settings: dict = None) -> None:
        if settings is None:
            settings = {}
        else:
            if not isinstance(settings, dict):
                raise TypeError("Settings must be dictionary.")

        # Open and read the JSON file
        with open("../solution/settings.init", "r", encoding="UTF-8") as json_file:
            json_data = json.load(json_file)

        self.settings = Settings(json_data["token"], json_data["organization"])

        if "telegram_bot_token" in json_data:
            self.settings.telegram_token = json_data["telegram_bot_token"]
        if "telegram_chat_id" in json_data:
            self.settings.telegram_chat_id = json_data["telegram_chat_id"]

        if settings.get("token"):
            self.settings.token = settings["token"]
        if settings.get("organization"):
            self.settings.organization = settings["organization"]

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Basic " + b64encode(f":{self.settings.token}".encode()).decode()
        }

        self.bot = telebot.TeleBot(self.settings.telegram_token)

        # define headers for json patch that used in create and update work item
        self.__json_patch_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json-patch+json",
            "Authorization": "Basic " + b64encode(f":{self.settings.token}".encode()).decode()
        }

        self.client: Client = Client(
            base_url=f"https://dev.azure.com/{self.settings.organization}/",
            headers=headers,
            follow_redirects=True,
            default_encoding="utf-8",
            timeout=15.0,
        )

    def create_project(self, name: str, description: str):
        """ Create project on Azure DevOps organization. """

        if not isinstance(name, str) or not isinstance(description, str):
            raise TypeError("Name and description must be strings.")

        data = {"name": name,
                "description": description,
                "visibility": "private",
                "capabilities": {"versioncontrol": {"sourceControlType": "Git"},
                                 "processTemplate":
                                     {"templateTypeId": "6b724908-ef14-45cf-84f8-768b5384da45"}},
                "processTemplate": {"templateTypeId": "6b724908-ef14-45cf-84f8-768b5384da45"}}

        response = self.client.post("/_apis/projects?api-version=7.0",
                                    json=data)

        if response.status_code == 202:
            # since create response have just link of new project
            # we need to get project info to make our response
            get_project_response = self.client.get(
                f"/_apis/projects/{name}?api-version=7.0")

            json_response = get_project_response.json()
            response = {
                "id": json_response["id"],
                "name": json_response["name"],
            }

            if self.settings.telegram_token and self.settings.telegram_chat_id:
                self.__send_message(f"New project '{name}' created on your Azure organization "
                                    f"'{self.settings.organization}'.")

            return Success(message=f"Project '{name}' created successfully.", response=response,
                           status_code=202)
        if response.status_code in [203, 401]:
            return Error(message="you have authorization problem, recheck your token.",
                         status_code=response.status_code)
        if response.status_code == 400:
            return Error(message=f"Project '{name}' is already exist.",
                         status_code=response.status_code)

        return Error(message=f"Error occurred with code {response.status_code}.",
                     status_code=response.status_code)

    def list_projects(self) -> Success | Error:
        """ List all projects on Azure DevOps organization. """

        get_response = self.client.get("/_apis/projects?api-version=7.0")

        if get_response.status_code == 200:
            json_response = get_response.json()
            if json_response["count"] != 0:
                result_response = {}
                i = 1
                for response in json_response["value"]:
                    result_response.update({i: response["name"]})
                    i += 1
                return Success(message="Projects listed successfully.", response=result_response,
                               status_code=get_response.status_code)

            return Success(message="There is no project in your organization.",
                           status_code=get_response.status_code)
        if get_response.status_code in [203, 401]:
            return Error(message="you have authorization problem, recheck your token.",
                         status_code=get_response.status_code)

        return Error(message=f"Error occurred with code {get_response.status_code}.",
                     status_code=get_response.status_code)

    def delete_project(self, project_name: str):
        """ Delete project from Azure DevOps organization. """

        if not isinstance(project_name, str):
            raise TypeError("Project name must be string.")

        project = self.get_project(project_name)

        if project.message == f"Project '{project_name}' not found.":
            return Error(message=f"Project '{project_name}' not found.",
                         status_code=404)
        if project.message == "you have authorization problem, recheck your token.":
            return Error(message="you have authorization problem, recheck your token.",
                         status_code=401)

        project_id = project.response["id"]

        response = self.client.delete(
            f"/_apis/projects/{project_id}?api-version=7.0")

        if response.status_code == 202:
            if self.settings.telegram_token and self.settings.telegram_chat_id:
                self.__send_message(
                    f"Project '{project_name}' deleted from your Azure organization "
                    f"'{self.settings.organization}'.")
            return Success(message=f"Project '{project_name}' "
                                   f"deleted successfully.", status_code=202)
        if response.status_code in [203, 401]:
            return Error(message="you have authorization problem, recheck your token.",
                         status_code=response.status_code)

        return Error(message=f"Error occurred with code {response.status_code}."
                             f"", status_code=response.status_code)

    def get_project(self, project_name: str):
        """ Get project info from Azure DevOps organization. """

        if not isinstance(project_name, str):
            raise TypeError("Project name must be string.")

        response = self.client.get(
            f"/_apis/projects/{project_name}?api-version=7.0")

        if response.status_code == 200:
            json_response = response.json()
            return Success("Project found.", {"id": json_response["id"],
                                              "name": json_response["name"],
                                              "url": json_response["url"]},
                           status_code=200)
        if response.status_code in [203, 401]:
            return Error(message="you have authorization problem, recheck your token.",
                         status_code=response.status_code)
        if response.status_code == 404:
            return Error(message=f"Project '{project_name}' not found.", status_code=404)

        return Error(f"Error occurred with code {response.status_code}.",
                     status_code=response.status_code)

    def create_work_item(self, project_id: str, work_item_type: str, work_item_value: str):
        """ Create work item on Azure DevOps organization. """

        if not isinstance(project_id, str) or \
                not isinstance(work_item_type, str) or not isinstance(work_item_value, str):
            raise TypeError("Project id, work item type and work item value must be strings.")

        body = [
            {
                "op": "add",
                "path": "/fields/System.Title",
                "from": None,
                "value": work_item_value
            }
        ]

        response = self.client.post(f"/{project_id}/_"
                                    f"apis/wit/workitems/${work_item_type}?api-version=7.0",
                                    json=body, headers=self.__json_patch_headers)

        if response.status_code == 200:
            json_response = response.json()
            result_response = {"title": json_response["fields"]["System.Title"],
                               "id": json_response["id"],
                               "type": json_response["fields"]["System.WorkItemType"]}

            if self.settings.telegram_token and self.settings.telegram_chat_id:
                self.__send_message(
                    f"Work item '{work_item_value}' created on your Azure organization "
                    f"'{self.settings.organization}'.")

            return Success(message=f"Work item '{work_item_value}' created successfully.",
                           response=result_response,
                           status_code=200)
        if response.status_code in [203, 401]:
            return Error(message="you have authorization problem, recheck your token.",
                         status_code=response.status_code)
        if response.status_code == 404:
            if f"Work item type {work_item_type} does not exist in project" \
                    in response.json()["message"]:
                return Error(message=f"Work item type '{work_item_type}' "
                                     f"does not exist in the project.",
                             status_code=404)

            return Error(message=f"Project '{project_id}' not found.", status_code=404)

        return Error(message=f"Error occurred with code {response.status_code}.",
                     status_code=response.status_code)

    def list_work_items(self, project_name: str):
        """ List work items on Azure DevOps organization. """

        if not isinstance(project_name, str):
            raise TypeError("Project id must be string.")

        body = {
            "query": f"Select * From WorkItems where [System.TeamProject] = '{project_name}'"
        }

        response = self.client.post(
            f"/{project_name}/_apis/wit/wiql?api-version=7.0",
            json=body)

        if response.status_code == 200:
            work_items = response.json()["workItems"]
            result_response = {}
            for work_item in work_items:
                # Query By Wiql just get the url of work item
                # So I use Get on the url to get the details of work item
                item = self.client.get(work_item["url"])

                item_json = item.json()
                result_response.update(
                    {item_json["id"]: {"title": item_json["fields"]["System.Title"],
                                       "type": item_json["fields"]["System.WorkItemType"]}})

            return Success(message="Work items listed successfully.", response=result_response,
                           status_code=200)
        if response.status_code in [203, 401]:
            return Error(message="you have authorization problem, recheck your token.",
                         status_code=response.status_code)
        if response.status_code == 404:
            return Error(message=f"Project '{project_name}' not found.", status_code=404)

        return Error(message=f"Error occurred with code {response.status_code}.",
                     status_code=response.status_code)

    def __get_work_item_id(self, project_name: str, work_item_title: str):
        """ Get work item id by name from Azure DevOps organization. """

        if not isinstance(project_name, str) or not isinstance(work_item_title, str):
            raise TypeError("Project id and work item title must be strings.")

        body = {
            "query": "Select id From WorkItems where System.Title = '" + work_item_title +
                     f"' and [System.TeamProject] = '{project_name}'"
        }

        response = self.client.post(
            f"/{project_name}/_apis/wit/wiql?api-version=7.0",
            json=body)

        if response.status_code == 200:
            if response.json()["workItems"]:
                return response.json()["workItems"][0]["id"]

            return "not found."
        if response.status_code in [203, 401]:
            return "you have authorization problem, recheck your token."

        return "not found."

    def update_work_item(self, project_name: str, work_item_title: str, new_work_item_title: str):
        """ Update work item on Azure DevOps organization. """

        if not isinstance(project_name, str) \
                or not isinstance(work_item_title, str) or \
                not isinstance(new_work_item_title, str):
            raise TypeError("Project id, work item title and new work item title must be strings.")

        work_item_id = self.__get_work_item_id(project_name, work_item_title)

        if work_item_id == "not found.":
            return Error(message=f"Work item '{work_item_title}' not found.", status_code=404)

        if work_item_id == "you have authorization problem, recheck your token.":
            return Error(message="you have authorization problem, recheck your token.",
                         status_code=401)

        body = [
            {
                "op": "replace",
                "path": "/fields/System.Title",
                "from": None,
                "value": new_work_item_title
            }
        ]

        response = self.client.patch(f"/"
                                     f"_apis/wit/workitems/{work_item_id}?api-version=7.0",
                                     json=body, headers=self.__json_patch_headers)
        if response.status_code == 200:

            if self.settings.telegram_token and self.settings.telegram_chat_id:
                self.__send_message(
                    f"Work item '{work_item_title}' updated to '{new_work_item_title}'"
                    f" in your Azure organization '{self.settings.organization}'.")
            return Success(message=f"Work item '{work_item_title}' "
                                   f"updated to '{new_work_item_title}'.",
                           status_code=200)

        return Error(message=f"Error occurred with code {response.status_code}.",
                     status_code=response.status_code)

    def delete_work_item(self, project_name: str, work_item_title: str):
        """ Delete work item on Azure DevOps organization."""

        if not isinstance(project_name, str) or not isinstance(work_item_title, str):
            raise TypeError("Project id and work item title must be strings.")

        work_item_id = self.__get_work_item_id(project_name, work_item_title)

        if work_item_id == "not found.":
            return Error(message=f"Work item '{work_item_title}' not found.", status_code=404)
        if work_item_id == "you have authorization problem, recheck your token.":
            return Error(message="you have authorization problem, recheck your token.",
                         status_code=401)

        response = self.client.delete(
            f"/{project_name}/"
            f"_apis/wit/workitems/{work_item_id}?api-version=7.0")

        if response.status_code == 200:

            if self.settings.telegram_token and self.settings.telegram_chat_id:
                self.__send_message(
                    f"Work item '{work_item_title}' deleted from your Azure organization "
                    f"'{self.settings.organization}'.")

            return Success(message=f"Work item '{work_item_title}' deleted successfully.",
                           status_code=200)
        if response.status_code in [203, 401]:
            return Error(message="you have authorization problem, recheck your token.",
                         status_code=response.status_code)
        if response.status_code == 404:
            return Error(message=f"Project '{project_name}' not found.", status_code=404)

        return Error(message=f"Error occurred with code {response.status_code}.",
                     status_code=response.status_code)

    def get_work_item(self, project_name: str, work_item_title: str):
        """ Get work item from Azure DevOps organization."""

        if not isinstance(project_name, str) or not isinstance(work_item_title, str):
            raise TypeError("Project id and work item title must be strings.")

        work_item_id = self.__get_work_item_id(project_name, work_item_title)

        if work_item_id == "you have authorization problem, recheck your token.":
            return Error(message="you have authorization problem, recheck your token.",
                         status_code=401)
        if work_item_id == "not found.":
            return Error(message=f"Work item '{work_item_title}' not found.",
                         status_code=404)

        response = self.client.get(f"/{project_name}"
                                   f"/_apis/wit/workitems/{work_item_id}?api-version=7.0")

        if response.status_code == 200:
            result = response.json()

            result_response = {
                "title": result["fields"]["System.Title"],
                "id": result["id"],
                "type": result["fields"]["System.WorkItemType"],
                "state": result["fields"]["System.State"]
            }

            return Success("Work item found.", result_response, 200)

        return Error(f"Error occurred with code {response.status_code}.", response.status_code)

    def close(self):
        """ Close connection to Azure DevOps organization."""
        self.client.close()

    def __send_message(self, mesaage: str):
        """ Send message to telegram chat."""

        if not isinstance(mesaage, str):
            raise TypeError("Message must be string.")

        self.bot.send_message(self.settings.telegram_chat_id, mesaage)
