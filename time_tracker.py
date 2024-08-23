import typer
import os
from dotenv import load_dotenv
import requests
import json
from datetime import datetime

load_dotenv()

app = typer.Typer()

API_KEY = os.getenv("API_KEY")
WORKSPACE_ID = os.getenv("WORKSPACE_ID")
HEADERS = {"X-Api-Key": API_KEY, "Content-Type": "application/json"}

# Fetch and store the USER_ID
def get_user_id():
    response = requests.get("https://api.clockify.me/api/v1/user", headers=HEADERS)
    response.raise_for_status()  # Raises an exception for 4xx/5xx responses
    user_data = response.json()
    return user_data["id"]

USER_ID = get_user_id()
# Helper function to make API requests
def clockify_request(method, endpoint, data=None):
    url = f"https://api.clockify.me/api/v1{endpoint}"
    response = requests.request(method, url, headers=HEADERS, json=data)
    response.raise_for_status()
    return response.json()


@app.command()
def logs():
    """View time logs for today."""
    today = datetime.utcnow().strftime("%Y-%m-%dT00:00:00Z")
    url = f"/workspaces/{WORKSPACE_ID}/user/{USER_ID}/time-entries?start={today}&end={today}"
    try:
        time_entries = clockify_request("GET", url)
        typer.echo("Today's time entries:")
        for entry in time_entries:
            start_time = entry['timeInterval']['start']
            end_time = entry['timeInterval'].get('end', 'In Progress')
            project_id = entry['projectId']
            typer.echo(f"Project {project_id}: {start_time} - {end_time}")
    except requests.exceptions.HTTPError as e:
        typer.echo(f"HTTP error occurred: {e}")


@app.command()
def logs_storage():
    """cache the logs per day in a folder."""

@app.command()
def time_spent():
    """Time spent per project."""




if __name__ == "__main__":
    app()
