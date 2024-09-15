#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import httplib2
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


def get_credential(service_account_file:str, scopes:list):
  return ServiceAccountCredentials.from_json_keyfile_name(service_account_file, scopes)

def get_service(service_account_file:str, scopes:list):
  return build('drive', 'v3', http=get_credential(scopes=scopes, service_account_file=service_account_file).authorize(httplib2.Http()))

def main():
  SCOPES = ['https://www.googleapis.com/auth/drive']
  SERVICE_ACCOUNT_KEY_FILE = 'backupautomation_service_account_key.json'

  service = get_service(scopes=SCOPES, service_account_file=SERVICE_ACCOUNT_KEY_FILE)

  file_metadata = {'name': 'notion_workspace.json', 'parents': ['drive_folder']} # Replace with your file name
  media = MediaFileUpload('./backup/notion_workspace.json') # Replace with your file path and mimetype
  file = service.files().create(body=file_metadata,
                                    media_body=media,
                                    fields='id').execute()
  print('File ID: %s' % file.get('id'))


if __name__ == '__main__':
  main()
