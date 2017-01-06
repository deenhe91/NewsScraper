#!/usr/bin/env python

# imports
import requests
import re
import json
from bs4 import BeautifulSoup
from newspaper import Article
from datetime import datetime
from newses import Guardian, BBC, WorldCrunch, EurActiv
from google.cloud import storage

members = ['mario draghi', 'vitor constancio', 'benoit coeure', 'yves mersche', 'sabine lautenschlager', 'peter praet']

# gather linKS

# PARSE
guardian = Gaurdian()
bbc = BBC()
wc = WorldCrunch()
euractiv = EurActiv()

sites = [guardian, bbc, wc, euractiv]

master_data = {}

for member in members:
	print('Find articles for {}...'.format(member))
	for site in sites:
		site.getlinks(member)
		member_data = site.parse()
		site_data = {site:member_data}
		master_data[site] = site_data

print('scrape complete. storing data.')

# STORE

bucket_name = ''

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))



