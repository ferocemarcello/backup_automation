import json
import time
import argparse
from notion_client import Client

def fetch_blocks(block_id:str, depth:int = 0, notion_client:str=None):
    """
    Recursively fetch the content of blocks from Notion API.
    """
    block_data = notion_client.blocks.children.list(block_id=block_id)
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
            block_item['children'] = fetch_blocks(block['id'], depth + 1)

        blocks.append(block_item)

    # Sleep to avoid hitting rate limits
    time.sleep(0.1)
    
    return blocks

def fetch_page(page_id:str, notion_client:str=None):
    """
    Fetch a single page and all of its blocks (recursively).
    """
    page_data = notion_client.pages.retrieve(page_id=page_id)
    page_title = page_data.get('properties', {}).get('title', {}).get('title', [{}])[0].get('plain_text', '')
    page_blocks = fetch_blocks(page_id)

    return {
        'id': page_id,
        'title': page_title,
        'blocks': page_blocks
    }

def fetch_database(database_id:str, notion_client:str=None):
    """
    Fetch all items from a Notion database, along with their contents.
    """
    database_data = notion_client.databases.query(database_id=database_id)
    database_results = database_data.get('results', [])
    database_items = []

    for item in database_results:
        page_id = item['id']
        database_items.append(fetch_page(page_id))

    return database_items

def fetch_all_pages_and_databases(notion_client:str=None):
    """
    Fetch all pages and databases in the workspace using the search endpoint.
    """

    # Search for all databases
    search_response = notion_client.search(query="", filter={"property": "object", "value": "database"})
    databases = search_response.get("results", [])

    # Search for all pages
    search_response = notion_client.search(query="", filter={"property": "object", "value": "page"})
    pages = search_response.get("results", [])

    return [page["id"] for page in pages], [db["id"] for db in databases]

def export_workspace_to_json(output_file:str = 'notion_workspace.json', notion_token:str=None):
    """
    Export the entire workspace (all pages and databases) to JSON.
    """
    workspace_data = {}

    # Initialize the Notion client
    notion_client = Client(auth=notion_token)

    # Fetch all pages and databases
    page_ids, database_ids = fetch_all_pages_and_databases(notion_client=notion_client)

    # Fetch pages
    for page_id in page_ids:
        page_data = fetch_page(page_id, notion_client=notion_client)
        workspace_data[page_data['title']] = page_data

    # Fetch databases
    for database_id in database_ids:
        database_data = fetch_database(database_id, notion_client=notion_client)
        workspace_data[f"Database_{database_id}"] = database_data

    # Write to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(workspace_data, f, ensure_ascii=False, indent=4)
    print(f"Exported workspace data to {output_file}")

if __name__ == "__main__":
    #python export_notion_workspace.py --output my_workspace.json --token your_notion_token

    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Export Notion workspace to JSON")
    parser.add_argument('--output', type=str, required=True, help="Output JSON file name")
    parser.add_argument('--token', type=str, required=True, help="Notion API token")

    # Parse the arguments
    args = parser.parse_args()

    # Call the function to export the workspace with the passed token and output file
    export_workspace_to_json(args.output, notion_token=args.token)
