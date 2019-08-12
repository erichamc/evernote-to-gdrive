import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
import os
import sys
from evernote_utils import *

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

def main():
    """Evernote to google drive exporter.
    Using some example code from the Google Drive API documentation.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API

    # Expect call: gdrive_uploader.py <path-to-notebook-folder>
    directory = sys.argv[1].replace('\ ',' ')
    if directory[-1] == '/':
            directory = directory[:-1]
    contents = os.listdir(directory)
    is_notebook = '.html' in ''.join(contents)
    # it's an exported notebook if it has .html files
    # otherwise we assume it contains notebook folders
    if is_notebook:
        nbpaths = [directory]
    else:
        nbpaths = [directory+'/'+d for d in os.listdir(directory) if os.path.isdir(directory+'/'+d)]
    
    for notebook_path in nbpaths:
        notebook_name = notebook_path.split('/')[-1]
        # Create notebook folder on gDrive
        print("Starting "+notebook_name+" notebook upload...")
        # TODO check if folder name already exists
        file_metadata = {
        'name': notebook_name,
        'mimeType': 'application/vnd.google-apps.folder'
        }
        file = service.files().create(body=file_metadata,
                                            fields='id').execute()
        nb_id = file.get('id') # for insertion to the correct folder
        note_paths = [notebook_path+'/'+n for n in os.listdir(notebook_path) if (n.split('.')[-1]=='html') and not (n.split('.')[0]=='index')]
        # iterate through notes
        for note in note_paths:
            # TODO check if folder/note already exists
            try:
                replace_images(note)
                creation, modification = extract_creation_modification(note)
                created_date = ''.join(creation.split('T')[0].split('-'))
                note_name = created_date+'_'+note.split('/')[-1].split('.html')[0]
                file_metadata = {
                'name': note_name,
                'parents': [nb_id],
                'mimeType': 'application/vnd.google-apps.document',#convert to gdoc
                'createdTime': creation,
                'modifiedTime': modification
                }
                media = MediaFileUpload(note,
                                        mimetype='text/html',
                                        resumable=True)
                file = service.files().create(body=file_metadata,
                                                    media_body=media,
                                                    fields='id').execute()
                print('Uploaded %s.' % note_name)
            except Exception as e:
                print('Failed to upload %s.' % note)
        print('Finished uploading %s!' % notebook_name)

if __name__ == '__main__':
    main()