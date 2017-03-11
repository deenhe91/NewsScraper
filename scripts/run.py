import requests
import json
import pandas as pd
from firebase import firebase
from datetime import datetime
from google.cloud import language 
from google.cloud import storage
import headline_search
import helper

# initiate firebase connection // Have this somewhere else.
base_url = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxx'

firebase = firebase.FirebaseApplication(base_url, None) 
all_sentiments = []

start_date = input('enter start date, i.e., 2017-01-01.\nIf unsure, enter "a" for automatic detection of last date: ')

def get_startdate():
	articles = firebase.get('{}data/articles'.format(base_url), None)
	max_date = max(articles.keys())
	return articles, max_date

if start_date == "a":
	articles, start_date = get_startdate()
	print("start date found : {}".format(start_date))

# WHEN SERVED, ALWAYS DETECT START_DATE AUTOMATICALLY
# think about time - don't want to miss certain articles that were published later in the last day
# start_date = get_startdate()

print("collecting articles from after : {}".format(start_date))

new_texts = []

count_ft = headline_search.FT(start_date, all_sentiments, new_texts, firebase)
count_g = headline_search.Guardian(start_date, all_sentiments, new_texts, firebase)
count_nyt = headline_search.NYT(start_date, all_sentiments, new_texts, firebase)
# save these article counts for histogram? TODO
total = count_g+count_ft+count_nyt
print("articles collected : {}".format(total))

# generate rolling sentiment df
srdf = helper.get_rolling_sentiment(articles)
helper.rolling_sentiment_to_firebase(srdf)
print("finished at {}".format(datetime.now()))
	
# add new text data to corpus

bucket_name = "xxxxxxxxxxx"
helper.download_blob(bucket_name, "data/corpus", "data/corpus.csv")
new_texts_df = pd.DataFrame(new_texts, columns=['date','text'])
old_corpus_df = pd.read_csv("data/corpus.csv")
new_corpus_df = pd.concat([old_corpus_df, new_texts_df], axis=0)

# store new csv to be uploaded to cloud storage
new_corpus_df.to_csv("data/new_corpus.csv")

# upload csv file to cloud storage
bucket_name = 'xxxxxxxxxxxx'
source_file_name = "data/new_corpus.csv"
now = datetime.strftime(datetime.now(), '%Y-%m-%d_%H:%M')
destination_blob_name = 'data/corpus'
helper.upload_blob(bucket_name, source_file_name, destination_blob_name)