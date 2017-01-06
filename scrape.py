# !/usr/bin/env python

# imports
import requests
import re
import json
# from bs4 import BeautifulSoup
# from newspaper import Article
from datetime import datetime
from newses import Guardian, BBC, WorldCrunch, EurActiv
from google.cloud import storage
from google.cloud import language

print('Imports successful. \n\n')

members = ['mario draghi', 'vitor constancio', 'benoit coeure', 'yves mersche', 'sabine lautenschlager', 'peter praet']

print('MEMBERS OF ECB BOARD:')
for member in members:
	print('{}\n'.format(member))

# COLLECT, PARSE
guardian = Guardian()
bbc = BBC()
wc = WorldCrunch()
euractiv = EurActiv()

sites = [guardian, bbc, wc, euractiv]

master_data = {}

# nested sites within members to avoid overscraping a site
print('Starting scrape...\n\n\n')

for member in members:
	print('Find articles for {}...'.format(member))
	for site in sites:
		site.getlinks(member)
		member_data = site.parse()
		# this will overwrite. therefore, doesn't add to dic, only creates for storage
		# store in cloud under 'date of scrape'?
		master_data[site][member] = member_data

with open('../data/master_data.json', 'w') as fp:
    json.dump(master_data, fp)

print('Scrape complete. storing data.')

# STORE

bucket_name = 'dove-hawk-data'
source_file_name = '../data/master_data.json'
now = datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M')
destination_blob_name = '{}-master_data'.format(now)

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))



