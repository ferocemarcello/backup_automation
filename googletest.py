#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Zero-touch enrollment quickstart sample.

This script forms the quickstart introduction to the zero-touch enrollemnt
customer API. To learn more, visit https://developer.google.com/zero-touch
"""

import sys
import httplib2
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# A single auth scope is used for the zero-touch enrollment customer API.
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_KEY_FILE = 'backupautomation_service_account_key.json'


def get_credential():
  """Creates a Credential object with the correct OAuth2 authorization.

  Uses the service account key stored in SERVICE_ACCOUNT_KEY_FILE.

  Returns:
    Credentials, the user's credential.
  """
  credential = ServiceAccountCredentials.from_json_keyfile_name(
    SERVICE_ACCOUNT_KEY_FILE, SCOPES)

  if not credential or credential.invalid:
    print('Unable to authenticate using service account key.')
    sys.exit()
  return credential


def get_service():
  """Creates a service endpoint for the zero-touch enrollment API.

  Builds and returns an authorized API client service for v1 of the API. Use
  the service endpoint to call the API methods.

  Returns:
    A service Resource object with methods for interacting with the service.
  """
  http_auth = get_credential().authorize(httplib2.Http())
  return build('drive', 'v3', http=http_auth)



def main():
  """Runs the zero-touch enrollment quickstart app.
  """
  # Create a zero-touch enrollment API service endpoint.
  service = get_service()

  file_metadata = {'name': 'backupautomation_service_account_key.json', 'parents': ['drive_folder']} # Replace with your file name
  media = MediaFileUpload('./backupautomation_service_account_key.json') # Replace with your file path and mimetype
  file = service.files().create(body=file_metadata,
                                    media_body=media,
                                    fields='id').execute()
  print('File ID: %s' % file.get('id'))


if __name__ == '__main__':
  main()
