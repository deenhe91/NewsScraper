#! /usr/bin/python

# imports
import requests
import re
import json
from datetime import datetime
from news import Guardian, BBC, WorldCrunch, EurActiv
from google.cloud import storage
from google.cloud import language
from multiprocessing.dummy import Pool as ThreadPool
import pandas as pd

print('Imports successful. \n\n')

members = ['ecb']

# COLLECT, PARSE
guardian = Guardian()
bbc = BBC()
wc = WorldCrunch()
euractiv = EurActiv()

site_map = {
	'bbc':bbc,
	'guardian': guardian,
	'worldcrunch': wc,
	'euractiv': euractiv
	}

sites = [bbc, guardian] # euractiv
site_names = ['bbc', 'guardian', 'euractiv'] #'guardian', 'wc'
master_data = {}

# nested sites within members to avoid overscraping a site
print('Starting scrape...\n') 

def getSiteData(site):
# create a helper function to wrap the site and data to make the mapping easier
	return site.getData(member)


def getMemberData(member):
	# for each site start a new thread
	print('Find articles for {}...'.format(member))

	# start thread pool and begin processing
	pool = ThreadPool(4) 
	results = pool.map(getSiteData, sites)
	pool.close() 
	# block until all the results have returned
	pool.join() 
	# results should contains the member data for each site
	return results


#  OLD NOW, NO CSV USED
def resultsToCsv(results):
	dates = []
	headlines = []
	texts = []
	authors = []
	sentiments = []
	time = []
	# dic = dictlist
	# d = dict
	for d in results:
		for date in d:
			for article in d[date]:
				# DO TUPLES, NOT SEPARATE LISTS, KEEP DATA TOGETHER!
				if type(article) == type({}):
					dates.append(date)
					texts.append(article['raw_text'])
					authors.append(article['author'])
					sentiments.append(article['sentiment']['score'])
					time.append(article['time'])

				elif type(article) == type([]):
					dates.append(date)
					texts.append(article[0]['raw_text'])
					authors.append(article[0]['author'])
					sentiments.append(article[0]['sentiment']['score'])
					time.append(article[0]['time'])
	
	df = pd.DataFrame()
# IF TUPLES, JUST DO: pd.DataFrame(tuple_list) - BOOM.
	df['DateTimeArticle'] = dates
	# df['Newspaper'] = 
	df['Author'] = authors
	df['Text'] = texts
	df['Sentiment'] = sentiments
	df['NextECBMeeting'] = 0
	df['URL'] = article_links
	# df['DataSource'] = 
	df['DataSourceGroup'] = "Scrape API"
	df['Entities'] = 0

	return df

member = input()
results = getMemberData(member)
df_results = resultsToCsv(results)


print('\nscrape complete, storing data...')
filename = 'data/scrape_results.csv'
df_results.to_csv(filename, delimiter=';')
print('\nresults table shape: '+str(df_results.shape))

# # STORE
bucket_name = 'xxxxxxxxxxxxx'
source_file_name = filename
now = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M')
destination_blob_name = 'scrape/{}-results_data.csv'.format(now)

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))

upload_blob(bucket_name, source_file_name, destination_blob_name)



