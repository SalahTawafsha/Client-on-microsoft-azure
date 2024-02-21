# Client on Microsoft Azure

this project is CLI application that can be used to manage a Microsoft Azure account. It is written in Python and
contains sync and async clients using Azure API. The application can be used to create and manage Projects.

## Features

### You can do the following as Main functions

- Create a new project
- get a project
- list all projects
- delete a project

### You can do the following for any project

- create a new work item
- get a work item
- update a work item
- delete a work item
- list all work items

### Additional features

- close connection to the server
- sync and async clients
- Telegram bot to interact with the application

## Testing

```bash
python -m pytest .\solution\unit_test\
```

## Installation

```bash
git clone https://github.com/SalahTawafsha/Client-on-microsoft-azure.git
pip install -r requirements.txt
```
- set your tokens and info in settings.init file
- set your token and organization of testing in files of unit_test folder (where you have ToDo)

## Usage

```bash
python main.py
```

### you will show the following

```
How would you like to run?
1. Sync client.
2. Async client.
3. Exit.
Enter your choice:
```

so can choose between sync and async clients or exit the application.

### if you choose sync or async client you will show the following

```
What would you like to do?
1. Create a new Project.
2. List all Projects.
3. Delete a Project.
4. Get Project.
5. Exit.
Enter your choice:
```

Choices 1, 2, 3 is clear, they use to manage the projects.

### 4. Get Project.

you will need to enter the project name to get the project, then you will show the following.

```
what would you like to do with the project '{project_name}'?
1. Create new work item.
2. List all work items.
3. Update a work item.
4. Delete a work item.
5. Get work item.
6. Return to main menu.
Enter your choice: 
```

Here you can manage the work items for the project.

