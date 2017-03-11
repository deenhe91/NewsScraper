from google.cloud import storage
from datetime import datetime
import pandas as pd
from firebase import firebase


firebase = firebase.FirebaseApplication('XXXXXXXXXXXXXXXXXXXXXXXXXXXXX', None)


#  CLOUD STORAGE THINGS

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

#  CORPUS CREATION

def get_weeks(df):
    """convert date strings to datetime and then isocalendar format so that rows can be grouped by week"""
    timestamps = [datetime.strptime(date, "%Y-%m-%d") for date in df['date']]
    weeks = [datetime.date(t).isocalendar()[:2] for t in timestamps]
    isodates = []

    for w in weeks:
        year = str(list(w)[0])
        week = str(list(w)[1])
        if len(week) == 1:
            week = '0'+week

        date = year+week
        isodates.append(date)

    df["week"] = isodates
    return list(set(isodates))

def groupby_week(df):
    print(df.shape)
    df = df.dropna()
    print(df.shape)
    corpus_weeks = []
    week_dates = list(set(df["week"]))
    week_groups = df.groupby("week")
    for w in week_dates:
        group = week_groups.get_group(w)
        week_text = ' '.join(group["text"])
        corpus_weeks.append(week_text)
    return corpus_weeks

# SENTIMENT PLOT

def get_rolling_sentiment(articles_from_firebase):
    dates = []
    sentiment = []
    for k, v in articles_from_firebase.items():
        for i in v:
            dates.append(k)
            sentiment.append(i['articleSentiment'])
    # sort firebase data into dataframe
    data = pd.DataFrame(list(zip(dates, sentiment)), columns=['date', 'sentiment'])

    # group by date to get mean daily values
    date_groups = data.groupby("date")
    daily_df = data.groupby("date").agg(["mean"])

    # put these mean daily values into a new table for calculating the rolling mean
    date_list = list(daily_df.index)
    sent_scores = list(daily_df.sentiment['mean'])
    rdf = pd.DataFrame(list(zip(date_list, sent_scores)), columns=['Day', 'Sentiment'])
    
    # sort values on datetime
    rdf['Datetime'] = [datetime.strptime(date, '%Y-%m-%d') for date in rdf['Day']]
    srdf = rdf.sort_values("Datetime")
    srdf = srdf.reset_index(drop=True)
    print(srdf.head())

    # compute rolling average
    rolling_av=[]
    for i in range(len(sent_scores)):
        j = i+30
        r = sum(srdf['Sentiment'][i:j])/35
        # print(srdf['Day'][i])
        rolling_av.append(r)
    srdf['Rolling'] = rolling_av

    return srdf


def rolling_sentiment_to_firebase(srdf):
    smooth_data = {}
    df = srdf.sort_values("Datetime")
    for i in range(len(df.Datetime)):
        smooth_data[i] = { "value" : df['Rolling'][i],
                           "date" : str(df['Datetime'][i])[:10] }
    firebase.put("/data/plots/sentiment", data=smooth_data, name="smooth")