from fastapi import FastAPI
import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv() 
app = FastAPI()

# JIRA Configuration (Update These)
JIRA_BASE_URL = "https://patatabullida987.atlassian.net/"  
JIRA_USERNAME = "patatabullida987@gmail.com"  
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
PROJECT_KEY = "SCRUM"  



# Function to fetch all Epics for the predefined project
def get_epics():
    jql = f'project = "{PROJECT_KEY}" AND issuetype = "Epic" ORDER BY created DESC'
    url = f"{JIRA_BASE_URL}/rest/api/3/search?jql={jql}&fields=summary"
    response = requests.get(url, auth=HTTPBasicAuth(JIRA_USERNAME, JIRA_API_TOKEN), verify=False)

    if response.status_code == 200:
        issues = response.json().get("issues", [])
        return {issue["key"]: issue["fields"]["summary"] for issue in issues}
    else:
        return {"error": f"Failed to fetch epics: {response.status_code}"}

# Function to fetch sub-incidents linked to an epic
def get_sub_incidents(epic_key):
    jql = f'parent = "{epic_key}" ORDER BY created DESC'
    url = f"{JIRA_BASE_URL}/rest/api/3/search?jql={jql}&fields=summary,status,assignee,created,updated,duedate"
    
    response = requests.get(url, auth=HTTPBasicAuth(JIRA_USERNAME, JIRA_API_TOKEN), verify=False)
    
    if response.status_code == 200:
        issues = response.json().get("issues", [])
        sub_incidents_list = []

        for issue in issues:
            fields = issue["fields"]
            sub_incidents_list.append({
                "Sub-Incident Key": issue["key"],
                "Title": fields.get("summary", "N/A"),
                "Status": fields["status"]["name"] if "status" in fields else "N/A",
                "Assignee": fields["assignee"]["displayName"] if fields.get("assignee") else "Unassigned",
                "Created": fields["created"][:10] if "created" in fields else "N/A",
                "Updated": fields["updated"][:10] if "updated" in fields else "N/A",
                "Due Date": fields.get("duedate", "N/A")
            })
        
        return sub_incidents_list
    else:
        return {"error": f"Failed to fetch sub-incidents: {response.status_code}"}

@app.get("/")
def read_root():
    return {"message": "JIRA API is running!"}

@app.get("/epics")
def fetch_epics():
    return get_epics()

@app.get("/sub-incidents/{epic_key}")
def fetch_sub_incidents(epic_key: str):
    return get_sub_incidents(epic_key)