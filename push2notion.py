import logging
import time
from datetime import datetime, timedelta
import requests
from notion_client import Client
import os

notion_token = os.environ['NOTION_API']
database_id = 'a05b2e9a2a38458db15a682ce03e9a4c'


def retrieve_task_title(notion_token, database_id):
    """only for test purpose"""
    client = Client(auth=notion_token, log_level=logging.ERROR)
    # print(client)
    response = client.databases.query(
        database_id=database_id,
        filter={
            "property": "Due",
            "date": {
                "on_or_before": datetime.now().strftime("%Y-%m-%d")
            }
        })
    task_name = response['results'][1]['properties']['Task name']['title']
    # Retrieve all the plain_text from the task title and concatenate them
    task_title = ''.join([part['plain_text'] for part in task_name])

    whole_task = response['results'][1]
    return task_title, whole_task
    # print(task_title)
    # print(task_name)


def parse_notion_response(response):
    # Initialize an empty dictionary for the parsed data
    parsed_data = {}

    # Task name
    task_name = response.get('properties',
                             {}).get('Task name',
                                     {}).get('title',
                                             [{}])[0].get('plain_text', '')
    parsed_data['Task Name'] = task_name

    # Urgency and Importance (assuming you only want the names of selected options)
    parsed_data['Urgency'] = [
        item['name'] for item in response.get('properties', {}).get(
            'urgency', {}).get('multi_select', [])
    ]
    parsed_data['Importance'] = [
        item['name'] for item in response.get('properties', {}).get(
            'Importance', {}).get('multi_select', [])
    ]

    # Assignee details
    assignees = response.get('properties', {}).get('Assignee',
                                                   {}).get('people', [])
    parsed_data['Assignees'] = [{
        'name':
        person.get('name', ''),
        'email':
        person.get('person', {}).get('email', '')
    } for person in assignees]

    # Status
    status = response.get('properties', {}).get('Status',
                                                {}).get('status',
                                                        {}).get('name', '')
    parsed_data['Status'] = status

    # Due date
    due_date = response.get('properties', {}).get('Due',
                                                  {}).get('date',
                                                          {}).get('start', '')
    parsed_data['Due Date'] = due_date

    # Urls
    parsed_data['Notion URL'] = response.get('url', '')
    parsed_data['Public URL'] = response.get('public_url', '')

    return parsed_data


# title, whole = retrieve_task_title(notion_token, database_id)
# parsed_response = parse_notion_response(whole)
# print(whole)
# print(parsed_response)


def insert_page(client: Client, database_id: str,
                task_title: str) -> None | str:
    '''Insert a page with a given task title and status set to "Inboxed".'''
    parent = {"database_id": database_id, "type": "database_id"}

    properties = {
        'Task name': {
            'id':
            'title',
            'type':
            'title',
            'title': [{
                'type': 'text',
                'text': {
                    'content': task_title,
                    'link': None
                },
                'plain_text': task_title,
                'href': None
            }]
        },
        'Due': {
            'id': 'notion%3A%2F%2Ftasks%2Fdue_date_property',
            'type': 'date',
            'date': {
                'start':
                (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
                'end': None,
                'time_zone': None
            }
        },
    }
    response = client.pages.create(parent=parent, properties=properties)
    return response["id"]


# client = Client(auth=notion_token, log_level=logging.DEBUG)
# page = insert_page(client, database_id, "test page from replit 3")
# print(page)
