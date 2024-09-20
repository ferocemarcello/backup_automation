#!/usr/bin/env python
# -*- coding: utf-8 -*-
import httplib2
import argparse
import os
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


def get_credential(service_account_file:str, scopes:list):
  return ServiceAccountCredentials.from_json_keyfile_name(service_account_file, scopes)

def get_service(service_account_file:str, scopes:list):
  return build('drive', 'v3', http=get_credential(scopes=scopes, service_account_file=service_account_file).authorize(httplib2.Http()))

def find_existing_files(service, drive_folder_id: str, file_name: str) -> list:
    # List all files in the folder with the given name
    results = service.files().list(
        q=f"'{drive_folder_id}' in parents and name='{file_name}'",
        spaces='drive',
        fields="files(id, name, createdTime)",
        orderBy="createdTime desc"  # Order by createdTime in descending order (newest first)
    ).execute()

    items = results.get('files', [])
    
    # Return all items except the newest one (first in the sorted list)
    return items[1:] if len(items) > 1 else []

def delete_file(service, file_id: str):
    print(f"Deleting old file (ID: {file_id})")
    service.files().delete(fileId=file_id).execute()

def upload_file_to_drive(service, file_path: str, drive_folder_id: str):
    file_name = os.path.basename(file_path)
    file = service.files().create(body={'name': file_name, 'parents': [drive_folder_id]}, media_body=MediaFileUpload(file_path), fields='id').execute()
    print('File ID: %s' % file.get('id'))

    # Find and delete old file
    existing_files = find_existing_files(service=service, drive_folder_id=drive_folder_id, file_name=file_name)
    list(map(lambda x: delete_file(service, x["id"]), existing_files))

def main():
  #python upload_to_drive.py --folder_id <your_drive_folder_id> --file_path <path_to_your_file> --service_account <path_to_service_account_key_file>
  parser = argparse.ArgumentParser(description="Upload a file to Google Drive using a service account")
  parser.add_argument('--drive_folder_id', type=str, required=True, help="Google Drive folder ID")
  parser.add_argument('--file_path', type=str, help="Path to the file to upload")
  parser.add_argument('--folder_path', type=str, help="Path to the folder to upload")
  parser.add_argument('--service_account', type=str, required=True, help="Path to the service account key file (JSON)")
  
  args = parser.parse_args()

  # Ensure either --file_path or --folder_path is provided, but not both
  if not args.file_path and not args.folder_path:
      parser.error("You must provide either --file_path or --folder_path.")
  if args.file_path and args.folder_path:
      parser.error("You can provide only one of --file_path or --folder_path, not both.")
  
  # Define Google Drive API scopes
  SCOPES = ['https://www.googleapis.com/auth/drive']
  SERVICE_ACCOUNT_KEY_FILE = args.service_account  # Path to the service account key file

  # Get authenticated Google Drive service
  service = get_service(scopes=SCOPES, service_account_file=SERVICE_ACCOUNT_KEY_FILE)

  # Upload the file to Google Drive
  upload_file_to_drive(service=service, file_path=args.file_path, drive_folder_id=args.drive_folder_id)


if __name__ == '__main__':
  main()
