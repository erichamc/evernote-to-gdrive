# evernote-to-gdrive
EverNote note resource consolidation, creation date extraction and note renaming, and upload to Google Drive

The goal of this Evernote-to-GoogleDrive exporter is to go from Evernote notes to chronologically ordered Google Docs, preserving linked/inline media as much as possible.

### The main functions of this exporter are:

- Handle some media types that would otherwise fail to import to a Google Doc
    -- Convert inline note images from referenced files to URI data.
    -- Convert linked PDF files to 300dpi PNGs and then to URI images.
- Extract the creation date from notes and place it in the note name
- Create folders on Google Drive for each Evernote notebook
- Upload each note file to the corresponding notebook folder
    -- Set the Creation Date metadata of the note appropriately
    -- Tell Google Drive to convert the file to a Google doc
- Alert the user of any notes fail to upload (prints to the command line)

### An alternative usage (without setting up the Google Drive API client):
Convert notes and move them into a new folder for each notebook.
Then, the containing folder can be dragged and dropped into Google Drive.
For this to convert the notes to Google Docs upon upload, change settings:
(Instructions from Google Drive)
1. Using a computer, go to drive.google.com/drive/settings.
2. Next to "Convert Uploads," check the box.

Tested only on an OS X machine.

## Installation instructions

Assuming you have anaconda python:

```
conda install -c conda-forge poppler
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
pip install beautifulsoup4 pdf2image
```

Alternatively, install from requirements.txt.

Follow the Step 1 instructions to enable the Google Drive API:
https://developers.google.com/drive/api/v3/quickstart/python
Download the credentials.json file and place it in the cloned respository's folder.

## Usage example

First, create an empty folder (named, for example, "notebooks-folder") somewhere. Using the Evernote desktop client, export Evernote notebooks as HTML into this empty folder (Notebook tab -> Right click on a notebook -> Export Notes from "[name of notebook]" -> Save format html). You'll have to type in a name for each one of these notebooks as you save them. You should end up the folder "notebooks-folder" containing folders with the contents of each exported Evernote notebook.

Then, in the command line:
```
$ cd /path/to/the/repository
$ python evernote_to_gdrive.py /path/to/folder/containing/notebook-folder
```
If it's the first time you do this, Google will pop up a browser window for you to log into your account and allow the script to make changes. After doing so, notebooks will begin uploading.

Alternatively (not using the Google Drive API client):
Create another empty folder for the converted notebooks to be output to. Then:
```
$ cd /path/to/the/repository
$ python consolidate_and_rename.py /path/to/folder/containing/notebook-folder /path/to/output/folder 
```
## Caveates

Currently, if the upload fails on a particular note, the exporter can't be easily rerun to retry an upload.

There isn't much robustness built in to the automatic uploading -- if it fails partway through, you might need to clean out the Google Drive and the exported note folders and start over.

Inline images and linked PDF files should convert appropriately. Other linked files will not and will not be uploaded using this exporter. Links will appear in the Google Doc but will be broken.

Google Drive / Docs doesn't currently allow you to sort by Create Date, so for chronological order of the exported notes, sort by name. If you want to use last-modified date for new notes, consider making a subfolder within the notebook folder on Goolge Drive to contain the exported notes, sorted by name, and put new notes in the top level of the notebook folder, sorted by modification / viewing date.