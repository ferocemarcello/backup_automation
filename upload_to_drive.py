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

def find_existing_file(service, folder_id: str, file_name: str):
    results = service.files().list(
        q=f"'{folder_id}' in parents and name='{file_name}'",
        spaces='drive',
        fields="files(id, name)"
    ).execute()

    items = results.get('files', [])
    return items[0] if items else None

def delete_file(service, file_id: str):
    print(f"Deleting old file (ID: {file_id})")
    service.files().delete(fileId=file_id).execute()

def upload_file_to_drive(service, file_path: str, file_name: str, folder_id: str):
    file = service.files().create(body={'name': file_name, 'parents': [folder_id]}, media_body=MediaFileUpload(file_path), fields='id').execute()
    print('File ID: %s' % file.get('id'))

    # Find and delete old file
    existing_file = find_existing_file(service=service, folder_id=folder_id, file_name=file_name)
    if existing_file and existing_file['id'] != file.get('id'):
        delete_file(service, existing_file['id'])

def main():
  #python upload_to_drive.py --folder_id <your_drive_folder_id> --file_path <path_to_your_file> --file_name <your_file_name> --service_account <path_to_service_account_key_file>
  parser = argparse.ArgumentParser(description="Upload a file to Google Drive using a service account")
  parser.add_argument('--folder_id', type=str, required=True, help="Google Drive folder ID")
  parser.add_argument('--file_path', type=str, required=True, help="Path to the file to upload")
  parser.add_argument('--file_name', type=str, default=None, help="Name of the file to upload to Google Drive")
  parser.add_argument('--service_account', type=str, required=True, help="Path to the service account key file (JSON)")
  
  args = parser.parse_args()
  if args.file_name is None:
    args.file_name = os.path.basename(args.file_path)

  # Define Google Drive API scopes
  SCOPES = ['https://www.googleapis.com/auth/drive']
  SERVICE_ACCOUNT_KEY_FILE = args.service_account  # Path to the service account key file

  # Get authenticated Google Drive service
  service = get_service(scopes=SCOPES, service_account_file=SERVICE_ACCOUNT_KEY_FILE)

  # Upload the file to Google Drive
  upload_file_to_drive(service=service, file_path=args.file_path, file_name=args.file_name, folder_id=args.folder_id)


if __name__ == '__main__':
  main()
