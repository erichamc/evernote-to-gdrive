import base64
import mimetypes
import os
import sys
from bs4 import BeautifulSoup as bs
from io import BytesIO
from pdf2image import convert_from_path

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
    images = soup.findAll('img', src=True)
    links = soup.findAll('a', href=True)
    all_media = [l for l in links if ('www' not in l['href'])]
    if images is not []:
        for image in images:
            img_data = img_to_data(resource_path+'/'+image['src'].split('/')[-1].replace('%20', ' '))
            image['src'] = img_data
            image['width'] = "500"
            image['height'] = "500"
    if all_media is not []:
        for media in all_media:
            mpath = resource_path+'/'+media['href'].split('/')[-1].replace('%20', ' ')
            if (media['href'].split('.')[-1] == 'pdf') and ('resources' in media['href']):
                try:
                    images = convert_from_path(mpath, dpi=300)
                    buffered = BytesIO()
                    datas = []
                    for im in images: # in case of multipage pdf
                        im.save(buffered, format="png")
                        data = base64.encodestring(buffered.getvalue()).decode("utf-8").replace('\n', '')
                        media_data = u'data:%s;base64,%s' % ("image/png", data)
                        datas.append(media_data)
                    for i,d in enumerate(datas):
                        if d != '':
                            tag = soup.new_tag('img')
                            tag['src'] = media_data
                            tag['width'] = "500"
                            tag['height'] = "500"
                            if i == 1:
                                media.replace_with(tag)
                            else:
                                media.insert_before(tag)
                except:
                    print('Failed to convert pdf media in: %s' % fpath)

    with open(fpath, 'w') as f:
        f.write(str(soup))
    
