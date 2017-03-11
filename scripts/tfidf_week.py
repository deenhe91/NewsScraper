
# RUN ON COMPUTE ENGINE?

from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
from firebase import firebase
from datetime import datetime
import helper

base_url = 'https://xxxxxxxxxxxxxxxxxxxxxxx/'
#  import text from cloud storage
bucket_name = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
helper.download_blob(bucket_name, "data/corpus", "data/corpus.csv")


text_df = pd.read_csv("data/corpus.csv").sort_values('date')
text_df = text_df.ix[1:]
print(text_df.head())
checkpoint = input()

# get week number for each article
isoweeks = helper.get_weeks(text_df)
print(max(isoweeks))
checkpoint = input()

# if checkpoint == "break":
#     break

# GENERATE CORPUS
corpus_weeks = helper.groupby_week(text_df)
dates = list(set(text_df['date']))

# create the vectoriser, single words and two consecutive words (ngrams), stopwords english - can be improved with discussed financial dictionary
tf = TfidfVectorizer(analyzer='word', ngram_range=(1,2), min_df = 0, stop_words = 'english')
tfidf_matrix =  tf.fit_transform(corpus_weeks)
feature_names = tf.get_feature_names()

# should run every week, therefore only need to grab last week. However
# checkpoint measure should be in place here.
n = -1
# n = max(firebase.get(blah, none).keys()) ## TODO
current_week_tfidf = tfidf_matrix.todense()[n:]
word_id = 0
word_scores = []


for score in current_week_tfidf.tolist()[0]:
    if score > 0:
        word = feature_names[word_id]
        tup = (score*1000, word.encode("utf-8"))
        word_scores.append(tup)
    word_id += 1

word_scores.sort()

# CLEAN PHRASE, MULTIPLY SCORE BY 1000
# sort function sorts ascending, therefore last 50 words are stored.
# push new to firebase.. no need to save to file 
data = {}
i = 0
print(word_scores[-30:])
for score, word in word_scores[-50:]:
    data[i] = {"value": str(word).strip("b").strip("'"),
                "weight": 1000*int(score)}
    i+=1

firebase = firebase.FirebaseApplication(base_url, None)
firebase.put("/data/wordclouds/tfidf/weeks/{}".format(max(isoweeks)), data=data, name="words")


