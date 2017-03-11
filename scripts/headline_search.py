'''Uses headline APIs to grab news sources from a specified start dat. Works on the assumption that the period covered will be 1 week'''

import requests
import json
import pandas as pd
from firebase import firebase
from datetime import datetime
from google.cloud import language 
from google.cloud import storage
import headline_search
import helper

# Use Google Language API to quickly get sentiment analysis
def getSentiment(text):
    language_client = language.Client()
    document = language_client.document_from_text(text)
    sentiment = document.analyze_sentiment()
    return sentiment.sentiment.score


# Finanacial Times headline API
def FT(start_date, all_sentiments, new_texts, firebase):
    count = 0
    # MOVE CREDENTIALS
    apiKey = 'xxxxxxxxxxx'
    apiUrl = 'http://api.ft.com/content/search/v1?apiKey='+apiKey
    # Request: Hard code Mario Draghi
    search_term = 'Mario Draghi'
    body = {
        'queryString': search_term,
        'queryContext':{
        'curations': ['ARTICLES']},
        'resultContext' : {
        'aspects' :[  'title', 'summary', 'lifecycle' ],
            }
        }
    r = requests.post(apiUrl, data=json.dumps(body))
    r = json.loads(r.text)
    results = r['results'][0]['results']
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    
    for i in results:
        article_date = datetime.strptime(i['lifecycle']['initialPublishDateTime'][:10], "%Y-%m-%d")
        string_date = str(article_date)

        if article_date > start_date:
            date = datetime.date(article_date)
            raw_text = i['title']['title'] + " " + i['summary']['excerpt']
            print("RAW TEXT : {}".format(raw_text))
            sentiment = getSentiment(raw_text)
            all_sentiments.append((date, sentiment))
            data = {"articleLink" : i['apiUrl'],
                    "articleSentiment" : sentiment,
                    "articleSite" : "The Financial Times",
                    # NO NEED TO STORE RAW_TEXT IN FIREBASE
                    # "articleText" : raw_text,
                    "articleHeadline" : i['title']['title'],
                    "dataSource" : "TheFinancialTimesAPI",
                    "dataSourceGroup" : "KeywordAPI"}

            new_texts.append((str(article_date)[:10], raw_text))

            base_url = 'XXXXXXXXXXXXXXXXXXXXXXXXXX'
            fb_result = firebase.get('{}data/articles/{}'.format(base_url, date), None)
            
            if fb_result:
                fb_result.append(data)
            else:
                fb_result = {0:data}
            resp = firebase.put('/data/articles', data=fb_result, name=str(article_date)[:10])
            count =+ 1
    return count

### Guardian headlines
def Guardian(start_date, all_sentiments, new_texts, firebase): # format YYYY-MM-DD
    count = 0
    # MOVE CREDENTIALS
    apiKey = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    apiUrl = "http://content.guardianapis.com/search?section=business&from-date={}&order-by=newest&page-size=100&q='ecb'%2C%20'mario%20draghi'%2C%20'draghi'&api-key=".format(start_date)+apiKey
    result_dic = requests.get(apiUrl).text

    # if live blog, remove " - as it happened" from 'webTitle' text

    for result in json.loads(result_dic)['response']['results']:        
        url = result['webUrl']
        title = result['webTitle']
        date = str(result['webPublicationDate'])[:10]

        sentiment = getSentiment(title)
        all_sentiments.append((date, sentiment))
        data = {"articleLink" : url,
                "articleSentiment" : sentiment,
                "articleSite" : "Guardian",
                # "articleText" : title,
                "articleHeadline" : title,
                "dataSource" : "GuardianAPI",
                "dataSourceGroup" : "KeywordAPI"}
        
        new_texts.append((date, title))

        fb_result = firebase.get('xxxxxxxxxxxxxxxxxxxxxxxxxxx'.format(date), None)
        if fb_result:
            fb_result.append(data)
        else:
            fb_result = {0:data}

        resp = firebase.put('/data/articles', data=fb_result, name=date)
        count += 1
    return count


# NEW YORK TIMES HEADLINES
def NYT(start_date, all_sentiments, new_texts, firebase):
    count = 0
    begin_date = ''.join(start_date.split('-'))


    url = "https://api.nytimes.com/svc/search/v2/articlesearch.json?begin_date={}&sort=newest&q=mario+draghi&api-key=2d8efae7494643f09ae37dcf652a5eba".format(begin_date)
    r = requests.get(url).text
    response = json.loads(r)
    for doc in response['response']['docs']:
        title = doc['headline']['main']
        print("TITLE\n: {}".format(title))
        if 'article' in doc["document_type"]:
            other_text = doc['lead_paragraph']+" "+doc['snippet']
            all_text = title+" "+other_text
            URL = doc['web_url']
            sentiment = getSentiment(all_text)
            date = doc['pub_date'][:10]
            all_sentiments.append((date, sentiment))

            data = {"articleLink":URL, 
                        "articleSentiment": sentiment,
                        # "articleText": all_text,
                        "articleHeadline" : title,
                        "dataSource" : "NYTimesAPI",
                        "dataSourceGroup" : "KeywordAPI"}

            fb_result = firebase.get('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'.format(date), None)
            
            new_texts.append((date, all_text))

            if fb_result:
                fb_result.append(data)
            else:
                fb_result = {0:data}

            resp = firebase.put('/data/articles', data=fb_result, name=date)
            count += 1
    return count