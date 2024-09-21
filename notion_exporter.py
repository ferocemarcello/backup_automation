import json
import time
import argparse
import requests
import os

# Define the base URL for the Notion API
NOTION_API_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"  # Notion API version

def fetch_page(page_id, notion_token):
    """
    Fetch a single page and all of its blocks (recursively) using raw API requests.
    """
    endpoint = f"pages/{page_id}"
    page_data = make_notion_request(endpoint, notion_token)
    
    # Extract the title of the page
    page_title = ""
    if "properties" in page_data and "title" in page_data['properties']:
        page_title = page_data['properties']['title']['title'][0].get('plain_text', '')

    page_blocks = fetch_blocks(page_id, notion_token)

    return {
        'id': page_id,
        'title': page_title,
        'blocks': page_blocks
    }

def fetch_database(database_id, notion_token):
    """
    Fetch all items from a Notion database using raw API requests.
    """
    endpoint = f"databases/{database_id}/query"
    database_data = make_notion_request(endpoint, notion_token, method="POST")
    database_results = database_data.get('results', [])
    database_items = []

    for item in database_results:
        page_id = item['id']
        database_items.append(fetch_page(page_id, notion_token))

    return database_items

def make_notion_request(endpoint, notion_token, method="GET", payload=None, params=None):
    """
    Makes a raw HTTP request to the Notion API.
    """
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION
    }
    
    url = f"{NOTION_API_URL}/{endpoint}"

    if method == "GET":
        response = requests.get(url, headers=headers, params=params)
    elif method == "POST":
        response = requests.post(url, headers=headers, json=payload)
    
    response.raise_for_status()
    return response.json()

def fetch_blocks(block_id:str, notion_token:str, depth=0):
    """
    Recursively fetch the content of blocks using raw API requests.
    """
    endpoint = f"blocks/{block_id}/children"
    block_data = make_notion_request(endpoint, notion_token)
    block_results = block_data.get('results', [])
    blocks = []

    for block in block_results:
        block_type = block['type']
        block_content = block[block_type]
        block_item = {
            'id': block['id'],
            'type': block_type,
            'content': block_content,
        }

        # If the block has children, recursively fetch them
        if block.get('has_children'):
            block_item['children'] = fetch_blocks(block['id'], notion_token, depth + 1)

        blocks.append(block_item)

    # Sleep to avoid hitting rate limits
    time.sleep(0.1)
    
    return blocks

def fetch_all_pages_and_databases(notion_token:str):
    """
    Fetch all pages and databases in the workspace using the search endpoint.
    """
    search_endpoint = "search"
    
    # Search for all databases
    payload = {"query": "", "filter": {"property": "object", "value": "database"}}
    search_response = make_notion_request(search_endpoint, notion_token, method="POST", payload=payload)
    databases = search_response.get("results", [])

    # Search for all pages
    payload = {"query": "", "filter": {"property": "object", "value": "page"}}
    search_response = make_notion_request(search_endpoint, notion_token, method="POST", payload=payload)
    pages = search_response.get("results", [])

    return [page["id"] for page in pages], [db["id"] for db in databases]

def export_workspace_to_json(notion_workspace_path:str, notion_token:str):
    """
    Export the entire workspace (all pages and databases) to JSON.
    """
    workspace_data = {}

    # Fetch all pages and databases
    page_ids, database_ids = fetch_all_pages_and_databases(notion_token=notion_token)

    # Fetch pages
    for page_id in page_ids:
        page_data = fetch_page(page_id, notion_token)
        workspace_data[page_data['title']] = page_data

    # Fetch databases
    for database_id in database_ids:
        database_data = fetch_database(database_id, notion_token)
        workspace_data[f"Database_{database_id}"] = database_data

    workspace_folder=os.path.dirname(notion_workspace_path)
    if not os.path.exists(workspace_folder):
        os.makedirs(workspace_folder)

    # Write to JSON file
    with open(notion_workspace_path, 'w', encoding='utf-8') as f:
        json.dump(workspace_data, f, ensure_ascii=False, indent=4)
    print(f"Exported workspace data to {notion_workspace_path}")

if __name__ == "__main__":
    #python notion_exporter.py --notion_workspace_path "./backup/notion_workspace.json" --token your_notion_token

    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Export Notion workspace to JSON")
    parser.add_argument('--notion_workspace_path', type=str, required=True, help="Output JSON file path")
    parser.add_argument('--token', type=str, required=True, help="Notion API token")

    # Parse the arguments
    args = parser.parse_args()
    for arg in args._get_args():
        print(f"arg: {str(arg)}")

    # Call the function to export the workspace with the passed token and output file
    export_workspace_to_json(notion_workspace_path=args.notion_workspace_path, notion_token=args.token)
