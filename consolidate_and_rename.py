import os
import sys
from evernote_utils import *

def main():
   
    # Expect call: consolidate_and_rename.py <path-to-notebook-folder> <path-to-empty-output-folder>
    directory = sys.argv[1].replace('\ ',' ')
    outdir = sys.argv[2].replace('\ ',' ')
    if directory[-1] == '/':
            directory = directory[:-1]
    if outdir[-1] == '/':
            outdir = outdir[:-1]
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
        # Create notebook folder in outdir
        print("Starting "+notebook_name+" notebook export...")
        notebook_subfolder = outdir+'/'+notebook_name
        os.mkdir(notebook_subfolder)
        note_paths = [notebook_path+'/'+n for n in os.listdir(notebook_path) if (n.split('.')[-1]=='html') and not (n.split('.')[0]=='index')]
        # iterate through notes
        for note in note_paths:
            try:
                replace_images(note)
                creation, modification = extract_creation_modification(note)
                created_date = ''.join(creation.split('T')[0].split('-'))
                note_name = created_date+'_'+note.split('/')[-1].split('.html')[0]
                os.rename(note, notebook_subfolder+'/'+note_name)
                print('Exported %s.' % note_name)
            except Exception as e:
                print('Failed to export %s.' % note)
        print('Finished exporting %s!' % notebook_name)

if __name__ == '__main__':
    main()