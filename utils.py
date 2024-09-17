import vercel_blob
import dotenv
import os 
import logging
import json 
import time
from datetime import datetime

logging.basicConfig(filename='app.log', filemode='a+', format='%(name)s - %(asctime)s - %(levelname)-8s - %(message)s')
logger = logging.getLogger("utils")
logger.setLevel(logging.INFO)


def convert_timestamp_to_date(timestamp_str):
    timestamp = int(timestamp_str)
    time_struct = time.gmtime(timestamp)
    formatted_date = time.strftime('%d-%m-%Y', time_struct)
    return formatted_date


def list_all_blobs():
    blobs = vercel_blob.list()
    print(blobs)
    return blobs
