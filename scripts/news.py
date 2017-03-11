'''Scraper classes'''
import re
import json
import datetime
import requests
from bs4 import BeautifulSoup
from newspaper import Article
from google.cloud import language
import pandas as pd

#  STORE HEADLINES + LINKS AS TUPLE
#  ADD HEADLINE AND LINK TO STORED DATA
class NewspaperScraper:

	def __init__(self):
		self.dic = {}  # creates a new empty dic for each instance
		self.article_links = []  # creates a new empty list for each instance
		self.sentiment_data = {}
		self.entity_data = {}
		self.raw_text = ''
		self.titles = []

	def newspaper(self, url):
		article = Article(url)   
		try:
			article.download()
			article.parse()
			r_datetime = article.publish_date
			d = datetime.datetime.strftime(r_datetime, '%Y-%m-%d')
			t = datetime.datetime.strftime(r_datetime, '%H:%M:%S')
			self.raw_text = article.text
			
			if len(article.authors):
				author = article.authors[0]
			else:
				author = 'none'
			return d, t, self.raw_text, author
		except:
			print('newspaper scrape failed')
			return 'none', 'none', 'none', 'none'


	def googlify(self):
		language_client = language.Client()
		document = language_client.document_from_text(self.raw_text)
		
		sentiment = document.analyze_sentiment()
		self.sentiment_data = {'score':sentiment.score, 'magnitude':sentiment.magnitude}
	
		entities = document.analyze_entities()
		for entity in entities:
			self.entity_data[entity.name] = {'type':entity.entity_type, 
										'salience':entity.salience}
		return self.sentiment_data, self.entity_data
	

	def dictify(self, d, t, author):
		if d in self.dic:
			self.dic[d].append([{'time':t,
									'author':author,
									# 'headline' : self.
									'raw_text':self.raw_text, 
									'sentiment':self.sentiment_data,
									'entities':self.entity_data}])
		else:
			self.dic[d] = [{'time':t,
							'author':author,
							'raw_text':self.raw_text, 
							'sentiment':self.sentiment_data,
							'entities':self.entity_data}]
		return self.dic	

	def getData(self, name):
		links, titles = self.getlinks(name)
		return self.parse()




class Guardian(NewspaperScraper):
	
	base_url = 'http://www.theguardian.com' # same for every instance

	def __init__(self):
		NewspaperScraper.__init__(self)

	def getlinks(self, name):
		apiKey = '458f61b9-2ff0-4a3f-98a1-feff65660ca6'
		#  uses the api
		df = pd.DataFrame()
		split_name = '%20'.join(name.split())
		# start_date = '2001-01-01'
		dates = []
		
		for i in range(1,5):
			apiUrl = 'http://content.guardianapis.com/search?section=business&page={}&page-size=200&q={}&api-key={}'.format(i, split_name, apiKey)
			result_dic = requests.get(apiUrl).text
			print(i)
			
		#  result is a string => jsonify:
			for result in json.loads(result_dic)['response']['results']:
				# only grab articles (not videos, photo lists, etc.)
				
				if result['type'] == 'article':
					url = result['webUrl']
					title = result['webTitle']
					date = result['webPublicationDate']

					self.article_links.append(url)
					dates.append(date)
					self.titles.append(title)
			
			print('dates: '+str(len(dates)))
			print('titles: '+str(len(self.titles)))
		
		print('no. of guardian articles: '+str(len(self.article_links)))
		return self.article_links, self.titles


	def parse(self):
		if self.article_links == None:
			raise Exception.message('No links! Run getlinks() before parse()')
		i = 0
		for link in self.article_links:
			d, t, self.raw_text, author = self.newspaper(link)
			i += 1
			self.googlify()
			self.dictify(d, t, author)
			# print('\nlink complete\n')
		with open('data/guardian_data.json', 'w') as fp:
			json.dump(self.dic, fp)
		print('no. guardian articles: '+str(i))
		return self.dic




class WorldCrunch(NewspaperScraper):
	def __init__(self):
		NewspaperScraper.__init__(self)

	base_url = 'http://www.worldcrunch.com/' # same for every instance

	# and search url ?
	
	def getlinks(self, search_url):
		
		r = requests.get(search_url)
		soup = BeautifulSoup(r.text, 'lxml')

		block = soup.find_all("div",{"class":"row"})[4]

		for b in block.find_all("a"):
			if len(b['href'].split('/')) > 6 and b['href'] not in self.article_links:
				self.article_links.append(b['href'])

		return self.article_links#, self.titles

	
	def parse(self):
		if self.article_links == None:
			raise Exception.message('No links! Run getlinks() before parse()')

		for link in self.article_links:
			d, t, self.raw_text, author = self.newspaper(link)
			self.googlify()
			self.dictify(d, t, author)
		with open('data/wc_data.json', 'w') as fp:
			json.dump(self.dic, fp)

		return self.dic


class EurActiv(NewspaperScraper):
	def __init__(self):
		NewspaperScraper.__init__(self)

	base_url = 'http://www.euractiv.com'

	def getlinks(self, name):
		split_name = '+'.join(name.split())
		search_url = 'http://www.euractiv.com/?s={}'.format(split_name)
		soup = BeautifulSoup(requests.get(search_url).text, 'lxml')
		block = soup.find_all("div", {"class":"row"})[4]
		
		for b in block.find_all("a"):
			if len(b['href'].split('/')) > 6 and b['href'] not in self.article_links:
				self.article_links.append(b['href'])

		return self.article_links, self.titles

	def parse(self):
		if self.article_links == None:
			raise Exception.message("No links! Run 'getlinks()' before 'parse()'")
		i = 0
		for link in self.article_links:
			i += 1
			d, t, self.raw_text, author = self.newspaper(link)
			self.googlify()
			self.dictify(d, t, author)
		
		# with open('data/euractiv_data.json', 'w') as fp:
		# 	json.dump(self.dic, fp)
		print('no. euractiv articles: '+str(i))
		return self.dic

class TheFT(NewspaperScraper):
	def __init__(self):
		NewspaperScraper.__init__(self)


	def getPages(self, name):
		pages = []
		for i in range(6):
			body = {
			"queryString": "mario AND draghi",
			"resultContext" : {
				"offset" : i*100,
			 	"aspects" :[  "title", "summary", "lifecycle" ]
				}}
			r = requests.post(url, body=body)
			pages.append(r.text)
		summaries = []
		titles = []
		dates = []
		for page in pages:
			for r in response['results'][0]['results']:
				if len(r['summary']) > 0:
					summaries.append(r['summary']['excerpt'])
				else:
					summaries.append('none')
				titles.append(r['title']['title'])
				dates.append(r['lifecycle']['initialPublishDateTime'])
		
		df = pd.DataFrame()
		df['date'] = dates
		df['title'] = titles
		df['summary'] = summaries

		df.to_csv('ft-results.csv')
		return df


class BBC(NewspaperScraper):
	def __init__(self):
		NewspaperScraper.__init__(self)

	base_url = 'http://www.bbc.com/news'

	def getlinks(self, name):
		split_name = '+'.join(name.split())
		for i in range(2,10):
			search_url = 'http://www.bbc.co.uk/search?q={}&page={}'.format(split_name, i)

			r = requests.get(search_url)
			soup = BeautifulSoup(r.text, 'lxml')

			results = soup.find_all("section", {"id":"search-content"})
			headlines = soup.find_all('h1', {'itemprop':'headline'})
			links = []
			tmp = results[0].find_all("li")
			for i in range(len(tmp)):
				try:
					if tmp[i].find("a")['href'] not in self.article_links:
						links.append(tmp[i].find("a")['href'])
						self.titles(append(headlines[i]))
				except:
					pass

			self.article_links.extend(links)

		
		return self.article_links, self.titles

	def parse(self):
		if self.article_links == None:
			raise Exception.message("No links! Run 'getlinks()' before 'parse()'")
		i=0
		for link in self.article_links:

			if 'uk/programmes' not in link and 'uk/news/live/' not in link:
				i+=1
				
				# print(link)
				article = Article(link)
				article.download()
				article.parse()
				self.raw_text = article.text

				author = 'BBC News'
				r = requests.get(link).text
				soup = BeautifulSoup(r, 'lxml')
				try:
					date = datetime.datetime.strptime(soup.find("div", {"class":"date date--v2"})['data-datetime'], '%d %B %Y')
					d = datetime.datetime.strftime(date, '%Y-%m-%d')
					t = datetime.datetime.strftime(date, '%H:%S')
				except:
					try:
						date = datetime.datetime.strptime(soup.find("p", {"class":"date date--v1"}).find("strong").text, '%d %B %Y')
						d = datetime.datetime.strftime(date, '%Y-%m-%d')
						t = datetime.datetime.strftime(date, '%H:%S')
					except:
						print("can't find date")
				
				self.googlify()
				self.dictify(d, t, author)

		print('no. bbc articles: '+str(i))
		return self.dic









