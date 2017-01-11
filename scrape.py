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

from multiprocessing.dummy import Pool as ThreadPool 


print('Imports successful. \n\n')

members = ['mario draghi']
# , 'benoit coeure', 'yves mersche', 'sabine lautenschlager', 'peter praet'

print('MEMBERS OF ECB BOARD:')
for member in members:
	print('{}\n'.format(member))

# COLLECT, PARSE
guardian = Guardian()
bbc = BBC()
wc = WorldCrunch()
euractiv = EurActiv()

# Joe: Maybe not idiomatic python, but in javascript another way to do this would be to
# site = {
#   bbc: bbc,
#   guardian: guardian,
#   ...
# }
# and then make a list from the keys if you need to

sites = [bbc]
site_names = ['bbc'] #'guardian', 'wc'
master_data = {}

# nested sites within members to avoid overscraping a site
print('Starting scrape...\n\n\n') 

def getMemberData(member):
  # create a helper function to wrap the site and data to make the mapping easier
  def getSiteData(site):
    return site.getData(member)

  # for each site start a new thread
  print('Find articles for {}...'.format(member))

  # start thread pool and begin processing
  pool = ThreadPool(4) 
  results = pool.map(sites, getSiteData)

  pool.close() 
  # block until all the results have returned
  pool.join() 

  # results should contains the member data for each site
  return results


for member in members:
  data = getMemberData(member)
  # Joe: this needs to be changed
  # this will overwrite. therefore, doesn't add to dic, only creates for storage
  # store in cloud under 'date of scrape'?
  # if site_names[i] in master_data:
  #   master_data[site_names[i]][member] = member_data
  # else:
  #   master_data[site_names[i]] = {member:member_data}


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



