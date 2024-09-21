#!/bin/bash

# Input arguments
BITWARDEN_CLIENT_ID=$1
BITWARDEN_CLIENT_SECRET=$2
BITWARDEN_MASTER_PASSWORD=$3
BITWARDEN_VAULT_PATH=$4
NOTION_WORKSPACE_PATH=$5
NOTION_TOKEN=$6
DRIVE_FOLDER_ID=$7
GOOGLE_SERVICE_ACCOUNT_FILE=$8

# Docker build
echo -e "Building Docker image..."
sudo docker build -t backup_image .

# Run Bitwarden Exporter
echo -e "Running Bitwarden exporter..."
sudo docker run -v ./:/app backup_image bash ./bitwarden_exporter.sh $BITWARDEN_CLIENT_ID $BITWARDEN_CLIENT_SECRET $BITWARDEN_MASTER_PASSWORD $BITWARDEN_VAULT_PATH

# Run Notion Exporter
echo -e "Running Notion exporter..."
sudo docker run -v ./:/app backup_image python ./notion_exporter.py --notion_workspace_path $NOTION_WORKSPACE_PATH --token $NOTION_TOKEN

# Check if BITWARDEN_VAULT_PATH and NOTION_WORKSPACE_PATH are in the same directory
DIR_BITWARDEN=$(dirname "$BITWARDEN_VAULT_PATH")
DIR_NOTION=$(dirname "$NOTION_WORKSPACE_PATH")

if [ "$DIR_BITWARDEN" == "$DIR_NOTION" ]; then
    echo -e "Both Notion backup and workspace are in the same directory: $DIR_NOTION"
    # Uploading the whole folder to google drive
    echo -e "Uploading the whole folder $DIR_NOTION to google drive"
    sudo docker run -v ./:/app backup_image python ./upload_to_drive.py --drive_folder_id $DRIVE_FOLDER_ID --folder_path $DIR_NOTION --service_account $GOOGLE_SERVICE_ACCOUNT_FILE

else
    echo -e "Notion backup and workspace are in different directories."
    # Run commands for separate directories
    echo -e "Uploading Bitwarden vault to Google Drive..."
    sudo docker run -v ./:/app backup_image python ./upload_to_drive.py --drive_folder_id $DRIVE_FOLDER_ID --file_path $BITWARDEN_VAULT_PATH --service_account $GOOGLE_SERVICE_ACCOUNT_FILE
    echo -e "Uploading Notion workspace to Google Drive..."
    sudo docker run -v ./:/app backup_image python ./upload_to_drive.py --drive_folder_id $DRIVE_FOLDER_ID --file_path $NOTION_WORKSPACE_PATH --service_account $GOOGLE_SERVICE_ACCOUNT_FILE
fi

#./backup.sh BITWARDEN_CLIENT_ID BITWARDEN_CLIENT_SECRET BITWARDEN_MASTER_PASSWORD BITWARDEN_VAULT_PATH NOTION_WORKSPACE_PATH NOTION_TOKEN DRIVE_FOLDER_ID GOOGLE_SERVICE_ACCOUNT_FILE
