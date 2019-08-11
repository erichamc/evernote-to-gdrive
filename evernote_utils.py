import base64
import mimetypes
import os
import sys
from bs4 import BeautifulSoup as bs

class FileNotFoundError(Exception):
    pass


def img_to_data(path):
    """Convert a file (specified by a path) into a data URI."""
    if not os.path.exists(path):
        return ''
    mime, _ = mimetypes.guess_type(path)
    with open(path, 'rb') as fp:
        data = fp.read()
        data64 = base64.encodestring(data).decode("utf-8").replace('\n', '')
        return u'data:%s;base64,%s' % (mime, data64)

def extract_creation_modification(fpath):
    """ Takes a string html evernote, returns string tuple of dates.
    params: 
        fpath: filepath of note
    Output: String tuple: creation date, updated date
    """
    with open(fpath, 'r') as f:
        note = f.read()
    soup = bs(note, features="html.parser")
    created = [t for t in soup.findAll('meta') if '"created"' in str(t)][0]['content']
    created = created.split(' ')[0]+'T'+''.join(created.split(' ')[1:])
    updated =  [t for t in soup.findAll('meta') if '"updated"' in str(t)][0]['content']
    updated = updated.split(' ')[0]+'T'+''.join(updated.split(' ')[1:])
    return created, updated

def replace_images(fpath):
    """ Takes a path to a note and edits the note to insert image data.
    params:
        fpath: path to note
    Output: None, writes new note with image data
    """
    with open(fpath, 'r') as f:
        line1 = f.readline() # get rid of the first xml tag line
        note = f.read()
    note_name = fpath.split('/')[-1].split('.html')[0]
    resource_path = fpath+'.resources'
    # Find each image tag and replace with corresponding uri data
    soup = bs(note, features="html.parser")
    images = soup.findAll('img')
    links = soup.findAll('a')
    all_media = [l for l in links if ('www' not in l['href'])]
    if images is not []:
        for image in images:
            img_data = img_to_data(resource_path+'/'+image['src'].split('/')[-1].replace('%20', ' '))
            image['src'] = img_data
    if all_media is not []:
        for media in all_media:
            media_data = img_to_data(resource_path+'/'+media['href'].split('/')[-1].replace('%20', ' '))
            if media_data != '':
                tag = soup.new_tag('img')
                tag['src'] = media_data
                media.replace_with(tag)
    with open(fpath, 'w') as f:
        f.write(str(soup))
    
