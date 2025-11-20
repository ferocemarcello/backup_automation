# Backup Automation

This repository contains a set of scripts to automate the backup of your Bitwarden vault and Notion workspace, and upload them to Google Drive. The entire process is containerized using Docker for consistency and ease of deployment.

## Project Structure

*   `backup.sh`: The main script that orchestrates the entire backup process. It builds a Docker image, runs the exporters, and uploads the backups.
*   `bitwarden_exporter.sh`: A shell script to log in to Bitwarden, unlock the vault, and export its contents.
*   `notion_exporter.py`: A Python script that uses the Notion API to fetch all pages and databases from a specified workspace and exports them into a JSON file.
*   `upload_to_drive.py`: A Python script responsible for uploading files or folders to a designated Google Drive folder using a Google service account for authentication.
*   `dockerfile`: Defines the Docker image used to run the backup tools.
*   `requirements.txt`: Lists the Python dependencies for `notion_exporter.py` and `upload_to_drive.py`.

## Setup and Configuration

Before running the backup, you need to configure several environment variables and files.

### 1. Google Drive Service Account

To enable `upload_to_drive.py` to access your Google Drive, you need to set up a Google Service Account:

1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a new project or select an existing one.
3.  Navigate to "IAM & Admin" -> "Service Accounts".
4.  Click "Create Service Account", give it a name, and grant it the necessary permissions (at least "Storage Object Creator" for the folder you intend to upload to).
5.  After creation, click on the service account, go to the "Keys" tab, and "Add Key" -> "Create new key" -> "JSON". This will download a JSON file.
6.  Rename this downloaded JSON file to something like `service_account.json` and place it in the root of this repository, or specify its path when running `backup.sh`.

### 2. Notion Integration

To backup your Notion workspace, you need a Notion integration token:

1.  Go to your Notion workspace settings -> "Integrations" -> "Develop your own integrations".
2.  Click "New integration", give it a name, and select the workspace it can access.
3.  Copy the "Internal Integration Token". This will be your `NOTION_TOKEN`.
4.  Share the specific pages/databases you want to back up with this integration by inviting it to them.

### 3. Bitwarden Credentials

For Bitwarden export, you need your client ID, client secret, and master password:

1.  Log in to your Bitwarden web vault.
2.  Go to "Settings" -> "Account Actions" -> "API Keys".
3.  Generate your API Key. This will provide you with a `client_id` and `client_secret`.
4.  Your Bitwarden master password will also be required.

## How to Run

The `backup.sh` script is the entry point for the entire process. It takes several arguments corresponding to the required credentials and paths.

```bash
./backup.sh \
    BITWARDEN_CLIENT_ID \
    BITWARDEN_CLIENT_SECRET \
    BITWARDEN_MASTER_PASSWORD \
    BITWARDEN_VAULT_PATH \
    NOTION_WORKSPACE_PATH \
    NOTION_TOKEN \
    DRIVE_FOLDER_ID \
    GOOGLE_SERVICE_ACCOUNT_FILE
```

**Arguments:**

*   `BITWARDEN_CLIENT_ID`: Your Bitwarden API Client ID.
*   `BITWARDEN_CLIENT_SECRET`: Your Bitwarden API Client Secret.
*   `BITWARDEN_MASTER_PASSWORD`: Your Bitwarden master password.
*   `BITWARDEN_VAULT_PATH`: The desired local path (e.g., `./backups/bitwarden_vault.json`) where the Bitwarden vault will be exported.
*   `NOTION_WORKSPACE_PATH`: The desired local path (e.g., `./backups/notion_workspace.json`) where the Notion workspace JSON will be saved.
*   `NOTION_TOKEN`: Your Notion integration token.
*   `DRIVE_FOLDER_ID`: The ID of the Google Drive folder where you want to upload your backups. You can find this in the URL when you open the folder in Google Drive (e.g., `https://drive.google.com/drive/folders/THIS_IS_THE_ID`).
*   `GOOGLE_SERVICE_ACCOUNT_FILE`: The path to your Google Service Account JSON key file (e.g., `./service_account.json`).

**Example Usage:**

```bash
./backup.sh \
    "your_bw_client_id" \
    "your_bw_client_secret" \
    "your_bw_master_password" \
    "./backups/bitwarden_vault.json" \
    "./backups/notion_workspace.json" \
    "secret_notion_token" \
    "google_drive_folder_id" \
    "./service_account.json"
```

The script will:
1.  Build a Docker image named `backup_image`.
2.  Run the Bitwarden exporter inside the Docker container.
3.  Run the Notion exporter inside the Docker container.
4.  If `BITWARDEN_VAULT_PATH` and `NOTION_WORKSPACE_PATH` resolve to the same directory, that entire directory will be uploaded to Google Drive. Otherwise, each file will be uploaded individually.

## Docker

The `dockerfile` sets up a Python environment with the necessary dependencies for the Notion and Google Drive exporters.

```dockerfile
# Dockerfile content would go here
```