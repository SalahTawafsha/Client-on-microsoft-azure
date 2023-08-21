""" Async Azure Client module. """
from httpx import AsyncClient, BasicAuth
from solution.data_classes.data_classes import Success, Error
from solution.solution.azure_client import AzureClient
from solution.solution.telegram_bot import TelegramBot


class AsyncAzureClient(AzureClient):
    """ Async Azure Client class."""

    def __init__(self, settings: dict = None, telegram_bot: TelegramBot = None) -> None:
        super().__init__(settings, telegram_bot)

        self.client: AsyncClient = AsyncClient(
            base_url=f"https://dev.azure.com/{self.settings.organization}/",
            auth=BasicAuth("", self.settings.token),
            headers=self.headers,
            follow_redirects=True,
            default_encoding="utf-8",
            timeout=15.0,
        )

    async def create_project(self, name: str, description: str):
        """ Create project on Azure DevOps organization. """

        if not isinstance(name, str) or not isinstance(description, str):
            raise TypeError("Name and description must be strings.")

        data = AsyncAzureClient.create_project_data(name, description)

        response = await self.client.post(AsyncAzureClient.END_POINTS["create_project"],
                                          json=data)

        return super().handle_create_project_response(response, name)

    async def list_projects(self) -> Success | Error:
        """ List all projects on Azure DevOps organization. """

        get_response = await self.client.get(AsyncAzureClient.END_POINTS["list_projects"])

        return AsyncAzureClient.handle_list_projects_response(get_response)

    async def delete_project(self, project_name: str):
        """ Delete project from Azure DevOps organization. """

        if not isinstance(project_name, str):
            raise TypeError("Project name must be string.")

        project = await self.get_project(project_name)

        result = AsyncAzureClient.check_get_project_response(project, project_name)

        if isinstance(result, Error):
            return result
        else:
            project_id = result

        response = await self.client.delete(
            AsyncAzureClient.END_POINTS['delete_project'].format(project_id=project_id))

        return super().handle_delete_project_response(response, project_name)

    async def get_project(self, project_name: str):
        """ Get project info from Azure DevOps organization. """

        if not isinstance(project_name, str):
            raise TypeError("Project name must be string.")

        response = await self.client.get(
            AsyncAzureClient.END_POINTS['get_project'].format(project_name=project_name))

        return AsyncAzureClient.handle_get_project_response(response, project_name)

    async def create_work_item(self, project_id: str, work_item_type: str, work_item_value: str):
        """ Create work item on Azure DevOps organization. """

        if not isinstance(project_id, str) or \
                not isinstance(work_item_type, str) or not isinstance(work_item_value, str):
            raise TypeError("Project id, work item type and work item value must be strings.")

        data = AsyncAzureClient.create_work_item_data(work_item_value)

        response = await self.client.post(
            AsyncAzureClient.END_POINTS['create_work_item'].format(project_id=project_id,
                                                                   work_item_type=work_item_type),
            json=data, headers=self._json_patch_headers)

        return super().handle_create_work_item_response(response, project_id, work_item_type,
                                                        work_item_value)

    async def list_work_items(self, project_name: str):
        """ List work items on Azure DevOps organization. """

        if not isinstance(project_name, str):
            raise TypeError("Project id must be string.")

        body = AsyncAzureClient.list_work_items_body(project_name)

        response = await self.client.post(
            AsyncAzureClient.END_POINTS['list_work_items'].format(project_name=project_name),
            json=body)

        if response.status_code == AsyncAzureClient.OK_STATUS_CODE:
            work_items = response.json()["workItems"]
            result_response = {}
            for work_item in work_items:
                # Query By Wiql just get the url of work item
                # So I use Get on the url to get the details of work item
                item = await self.client.get(work_item["url"])

                item_json = item.json()
                result_response.update(
                    {item_json["id"]: {"title": item_json["fields"]["System.Title"],
                                       "type": item_json["fields"]["System.WorkItemType"]}})

            return Success(message="Work items listed successfully.", response=result_response,
                           status_code=AsyncAzureClient.OK_STATUS_CODE)

        return AsyncAzureClient.handle_falied_list_work_items_response(response, project_name)

    async def _get_work_item_id(self, project_name: str, work_item_title: str):
        """ Get work item id by name from Azure DevOps organization. """

        if not isinstance(project_name, str) or not isinstance(work_item_title, str):
            raise TypeError("Project id and work item title must be strings.")

        body = {
            "query": "Select id From WorkItems where System.Title = '" + work_item_title +
                     f"' and [System.TeamProject] = '{project_name}'"
        }

        response = await self.client.post(
            format(AsyncAzureClient.END_POINTS['list_work_items'].format(project_name=project_name)), json=body)

        if response.status_code == AsyncAzureClient.OK_STATUS_CODE:
            if response.json()["workItems"]:
                return response.json()["workItems"][0]["id"]

            return "not found."
        if response.status_code in AsyncAzureClient.NON_AUTHORIZED_STATUS_CODES:
            return "you have authorization problem, recheck your token."

        return "not found."

    async def update_work_item(self, project_name: str, work_item_title: str,
                               new_work_item_title: str):
        """ Update work item on Azure DevOps organization. """

        if not isinstance(project_name, str) or not isinstance(work_item_title, str) \
                or not isinstance(new_work_item_title, str):
            raise TypeError("Project id, work item title and new work item title must be strings.")

        work_item = await self._get_work_item_id(project_name, work_item_title)

        result = AsyncAzureClient.update_work_item_body(work_item, work_item_title, new_work_item_title)

        if isinstance(result, Error):
            return result
        else:
            body = result

        response = await self.client.patch(AsyncAzureClient.END_POINTS['update_work_item']
                                           .format(project_name=project_name, work_item_id=work_item),
                                           json=body, headers=self._json_patch_headers)

        return super().handle_update_work_item_response(response, work_item_title,
                                                        new_work_item_title)

    async def delete_work_item(self, project_name: str, work_item_title: str):
        """ Delete work item on Azure DevOps organization."""

        if not isinstance(project_name, str) or not isinstance(work_item_title, str):
            raise TypeError("Project id and work item title must be strings.")

        work_item_id = await self._get_work_item_id(project_name, work_item_title)

        result = AsyncAzureClient.delete_work_item_body(work_item_id, work_item_title)

        if isinstance(result, Error):
            return result

        response = await self.client.delete(AsyncAzureClient.END_POINTS['delete_work_item']
                                            .format(project_name=project_name, work_item_id=work_item_id))

        return super().handle_delete_work_item_response(response, project_name, work_item_title)

    async def get_work_item(self, project_name: str, work_item_title: str):
        """ Get work item from Azure DevOps organization."""

        if not isinstance(project_name, str) or not isinstance(work_item_title, str):
            raise TypeError("Project id and work item title must be strings.")

        work_item_id = await self._get_work_item_id(project_name, work_item_title)

        result = AsyncAzureClient.delete_work_item_body(work_item_id, work_item_title)

        if isinstance(result, Error):
            return result

        response = await self.client.get(AsyncAzureClient.END_POINTS['get_work_item']
                                         .format(project_name=project_name, work_item_id=work_item_id))

        return AsyncAzureClient.handle_get_work_item_response(response)

    async def close(self):
        """ Close connection to Azure DevOps organization."""
        await self.client.aclose()
