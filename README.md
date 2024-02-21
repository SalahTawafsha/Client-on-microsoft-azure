# Client on Microsoft Azure

this project is CLI application that can be used to manage a Microsoft Azure account. It is written in Python and
contains sync and async clients using Azure API. The application can be used to create and manage Projects.

## features

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

## Installation

```bash
git clone https://github.com/SalahTawafsha/Client-on-microsoft-azure.git
pip install -r requirements.txt
```

## Usage
```bash
python main.py
```
### 1. you will show the following 
```bash
How would you like to run?
1. Sync client.
2. Async client.
3. Exit.
Enter your choice:
```
so can choose between sync and async clients or exit the application.

### 2. if you choose sync client you will show the following
```bash

