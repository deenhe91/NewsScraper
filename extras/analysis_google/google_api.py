import os
import requests
import sys
import json
from googleapiclient import discovery 
from oauth2client.client import GoogleCredentials 
import text_cleaning as cleaner


#  set up API
DISCOVERY_URL = 'https://language.googleapis.com/$discovery/rest?version=v1beta1'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'auth/google_secrets.json'

credentials = GoogleCredentials.get_application_default()
http = httplib2.Http()
credentials.authorize(http)

service = discovery.build('language', 'v1beta1', credentials=credentials, discoveryServiceUrl=DISCOVERY_URL)

# clean texts
text = 

text_body = cleaner.clean(text)

sentiment_request = service.documents().analyzeSentiment(
					body={
						'document': {
						'type': 'PLAIN_TEXT', # can use HTML
						'content': text_body
						}
					})

sentiment_response = sentiment_request.execute()


entity_request = service.documents()analyzeEntities(
					body={
						'document': {
						'type': 'PLAIN_TEXT',
						'content': text_body
						}
					})
entity_response = entity_request.execute()

if __name__ == '__main__':
    app.run(debug=True)

