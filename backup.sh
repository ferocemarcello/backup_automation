#!/bin/bash

# Input arguments
BITWARDEN_CLIENT_ID=$1
BITWARDEN_CLIENT_SECRET=$2
BITWARDEN_MASTER_PASSWORD=$3
FILE_NAME_NOTION=$4
NOTION_TOKEN=$5
DRIVE_FOLDER_ID=$6
BACKUP_FILE_PATH_BITWARDEN=$7
FILE_NAME_BITWARDEN=$9
GOOGLE_SERVICE_ACCOUNT_FILE=$8
BACKUP_FILE_PATH_NOTION=$10

# Docker build
echo -e "Building Docker image..."
sudo docker build -t backup_image .

# Run Bitwarden Exporter
echo -e "Running Bitwarden exporter..."
sudo docker run -v ./:/app backup_image bash ./bitwarden_exporter.sh $BITWARDEN_CLIENT_ID $BITWARDEN_CLIENT_SECRET $BITWARDEN_MASTER_PASSWORD

# Run Notion Exporter
echo -e "Running Notion exporter..."
sudo docker run -v ./:/app backup_image python ./notion_exporter.py --output $FILE_NAME_NOTION --token $NOTION_TOKEN

# Upload Bitwarden vault to Google Drive
echo -e "Uploading Bitwarden vault to Google Drive..."
sudo docker run -v ./:/app backup_image python ./upload_to_drive.py --folder_id $DRIVE_FOLDER_ID --file_path $BACKUP_FILE_PATH_BITWARDEN --file_name $FILE_NAME_BITWARDEN --service_account $GOOGLE_SERVICE_ACCOUNT_FILE

# Upload Notion workspace to Google Drive
echo -e "Uploading Notion workspace to Google Drive..."
sudo docker run -v ./:/app backup_image python ./upload_to_drive.py --folder_id $DRIVE_FOLDER_ID --file_path $BACKUP_FILE_PATH_NOTION --file_name $FILE_NAME_NOTION --service_account $GOOGLE_SERVICE_ACCOUNT_FILE

#./backup.sh BITWARDEN_CLIENT_ID BITWARDEN_CLIENT_SECRET BITWARDEN_MASTER_PASSWORD FILE_NAME_NOTION NOTION_TOKEN DRIVE_FOLDER_ID BACKUP_FILE_PAARDEN FILE_NAME_BITWARDEN GOOGLE_SERVICE_ACCOUNT_FILE DRIVE_FOLDER_ID BACKUP_FILE_PATH_NOTION FILE_NAME_NOTION GOOGLE_SERVICE_ACCOUNT_FILE
