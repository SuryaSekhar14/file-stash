import vercel_blob
import os 
import logging
import json 
import time
from datetime import datetime
import pprint

logging.basicConfig(filename='app.log', filemode='a+', format='%(name)s - %(asctime)s - %(levelname)-8s - %(message)s')
logger = logging.getLogger("utils")
logger.setLevel(logging.INFO)


def convert_timestamp_to_date(timestamp_str):
    timestamp = int(timestamp_str)
    time_struct = time.gmtime(timestamp)
    formatted_date = time.strftime('%d-%m-%Y', time_struct)
    return formatted_date


def iso_to_ddmmyy(iso_timestamp: str) -> str:
    # Parse the ISO timestamp
    dt_obj = datetime.strptime(iso_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    
    # Format to ddmmyy
    return dt_obj.strftime("%d-%m-%Y")


def list_all_blobs():
    '''
    List all blobs in the Blob storage
    '''
    hasMore = True
    blobs = []

    while hasMore == True:
        resp = vercel_blob.list()
        blobs.extend(resp.get('blobs'))
        hasMore = resp.get('hasMore')
        # pprint.pprint(resp)

    for i, blob in enumerate(blobs):
        blob['id'] = i + 1
        blob['filename'] = blob.get('contentDisposition').split('filename=')[1].replace('"', '')
        blob['uploadedAt'] = iso_to_ddmmyy(blob.get('uploadedAt'))

        blob_size = blob.get('size', 0)
        if blob_size < 1024:
            blob['size'] = f"{blob_size} B"
        elif blob_size < 1024 * 1024:
            blob['size'] = f"{blob_size / 1024:.2f} KB"
        else:
            blob['size'] = f"{blob_size / (1024 * 1024):.2f} MB"

    pprint.pprint(blobs)

    # Download blobs to cache
    for blob in blobs:
        filename = blob.get('filename')
        if filename not in os.listdir('cache'):
            logger.info(f"Downloading {filename} from Vercel Blob")
            vercel_blob.download_file(blob.get('url'), f'cache/{filename}')
        else:
            logger.info(f"{filename} already exists in cache")

    return blobs


def upload_file(file):
    '''
    Upload a file to the Blob storage
    '''
    filename = file.filename
    logger.info(f"Uploading file: {filename}")

    # Save the file to cache
    file.save(f'cache/{filename}')

    # Upload the file to Blob storage
    with open(f'cache/{filename}', 'rb') as f:
        print(type(f))
        vercel_blob.put(path = f'cache/{filename}', data = f.read(), options = {
            'addRandomSuffix': 'false',
        })

    return True


def 