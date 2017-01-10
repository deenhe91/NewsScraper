import re
import json
import datetime
import requests
from bs4 import BeautifulSoup
from newspaper import Article
from google.cloud import language

class NewspaperScraper:

	def __init__(self):
		self.dic = {}  # creates a new empty dic for each instance
		self.article_links = []  # creates a new empty list for each instance
		self.sentiment_data = {}
		self.entity_data = {}
		self.raw_text = ''

	def newspaper(self, url, authors='authors'):
		article = Article(url)   

		try:
			article.download()
			article.parse()
			r_datetime = article.publish_date
			d = datetime.strftime(r_datetime, '%Y-%m-%d')
			t = datetime.strftime(r_datetime, '%H:%M:%S')
			self.raw_text = article.text
			if authors =='authors':
			    author = article.authors[0]
			else:
			    author = 'none'
			
			return d, t, self.raw_text, author
		except:
			return 'none', 'none', 'none', 'none'

	def googlify(self):
		language_client = language.Client()
		document = language_client.document_from_text(self.raw_text)
		
		sentiment = document.analyze_sentiment()
		self.sentiment_data = {'score':sentiment.score, 'magnitude':sentiment.magnitude}
	
		entities = document.analyze_entities()
		for entity in entities:
			self.entity_data[entity.name] = {'type':entity.entity_type, 
										'salience':entity.salience, 
										'wiki':entity.wikipedia_url}
		return self.sentiment_data, self.entity_data
	

	def dictify(self, d, t, author):
		if d in self.dic:
			self.dic[d].append([{'time':t,
									'author':author,
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




class Guardian(NewspaperScraper):
	
	base_url = 'http://www.theguardian.com' # same for every instance

	def __init__(self):
		NewspaperScraper.__init__(self)



	def getlinks(self, name):
		apiKey = '458f61b9-2ff0-4a3f-98a1-feff65660ca6'

		#  uses the api unlike others
		split_name = '%20'.join(name.split())
		date = '2001-01-01'
		apiUrl = 'http://content.guardianapis.com/search?from-date={}&page-size=161&q={}&api-key={}'.format(date, split_name, apiKey)

		result_dic = requests.get(apiUrl).text
		
		#  result is a string > jsonify:
		for result in json.loads(result_dic)['response']['results']:
			# only grab articles (not videos, photo lists, etc.)
			if result['type'] == 'article' and result['sectionId'] != 'sport':
				url = result['webUrl']
				self.article_links.append(url)

		return self.article_links


	def parse(self):
		
		if self.article_links == None:
			raise Exception.message('No links! Run getlinks() before parse()')

		for link in self.article_links:
			d, t, author, self.raw_text = self.newspaper(link)
			self.googlify()
			self.dictify(d, t, author)
			with open('data/guardian_data.json', 'w') as fp:
				json.dump(self.dic, fp)

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

		return self.article_links

	
	def parse(self):
		if self.article_links == None:
			raise Exception.message('No links! Run getlinks() before parse()')

		for link in self.article_links:
			d, t, author, self.raw_text = self.newspaper(link)
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
		soup = BeautifulSoup(requests.get(search_url).text)
		block = soup.find_all("div", {"class":"row"})[4]
		
		for b in block.find_all("a"):
			if len(b['href'].split('/')) > 6 and b['href'] not in self.article_links:
				self.article_links.append(b['href'])

		return self.article_links

	def parse(self):
		if self.article_links == None:
			raise Exception.message("No links! Run 'getlinks()' before 'parse()'")

		for link in self.article_links:
			d, t, author, self.raw_text = self.newspaper(link)
			self.googlify()
			self.dictify(d, t, author)
			with open('data/euractiv_data.json', 'w') as fp:
				json.dump(self.dic, fp)

		return self.dic


class BBC(NewspaperScraper):
	def __init__(self):
		NewspaperScraper.__init__(self)

	base_url = 'http://www.bbc.com/news'

	def getlinks(self, name):
		split_name = '+'.join(name.split())
		for i in range(2,5):
			search_url = 'http://www.bbc.co.uk/search?q={}&page={}'.format(split_name, i)

			r = requests.get(search_url)
			soup = BeautifulSoup(r.text, 'lxml')

			results = soup.find_all("section", {"id":"search-content"})
			links = []
		
			for r in results[0].find_all("li"):
				if r.find("a")['href'] not in self.article_links:
					links.append(r.find("a")['href'])

			self.article_links.extend(links)

		
		return self.article_links  

	def parse(self):
		if self.article_links == None:
			raise Exception.message("No links! Run 'getlinks()' before 'parse()'")

		for link in self.article_links:
			try:
				article = Article(link)
				article.download()
				article.parse()
				self.raw_text = article.text

				author = 'BBC News'
				r = requests.get(link).text
				soup = BeautifulSoup(r, 'lxml')
				
				date = datetime.datetime.strptime(soup.find("div", {"class":"date date--v2"})['data-datetime'], '%d %B %Y')
				d = datetime.strftime(date, '%Y-%m-%d')
				t = datetime.strftime(date, '%H:%S')
				# d, t, author, raw_text = newspaper(link)
				self.googlify()
				self.dictify(d, t, author)
				with open('data/bbc_data.json', 'w') as fp:
					json.dump(self.dic, fp)
			except:
				pass








