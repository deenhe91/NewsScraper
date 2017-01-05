import subprocess

class NewspaperScraper():

	def __init__(self):
		self.dic = {}  # creates a new empty dic for each instance
		self.article_links = []  # creates a new empty list for each instance


	def newspaper(self, url, authors='authors'):
		article = Article(url)   

		try:
			article.download()
			article.parse()
			r_datetime = article.publish_date
			d = datetime.strftime(r_datetime, '%Y-%m-%d')
			t = datetime.strftime(r_datetime, '%H:%M:%S')
			raw_text = article.text
			if authors =='authors':
			    author = article.authors[0]
			else:
			    author = 'none'
		return d, t, raw_text, author
	except:
	return 'none', 'none', 'none', 'none'


	def dictify(self, d, t, author, raw_text):
		if d in self.dic:
			self.dic[d].extend([(author, t, raw_text)])
		else:
			self.dic[d] = [(author, t, raw_text)]
		return self.dic	
	
	def soupify(url):
		r = requests.get(url)
		soup = BeautifulSoup(r.text, 'lxml')
		return soup

	# def store():
		#  store everything in cloud storage



class Guardian(NewspaperScraper):
	
	base_url = 'http://www.theguardian.com' # same for every instance
	apiKey = '458f61b9-2ff0-4a3f-98a1-feff65660ca6'

	def __init__(self):
		self.article_links = []  # creates a new empty  for each instance


	def getlinks(self, name):
		#  uses the api unlike others
		split_name = '%20'.join(name.split())
		date = '2001-01-01'
		apiUrl = 'http://content.guardianapis.com/search?from-date={}&page-size=161&q={}&api-key={}'.format(date, split_name, apiKey)

		result_dic = requests.get(apiUrl).text[]
		
		for result in json.loads(result_dic.text)['response']['results']:

			if result['type'] == 'article' and result['section'] != 'sport':
				url = result['webUrl']
				self.article_links.append(url)

		return self.article_links


	def parse(self):
		
		if self.article_links = None:
			raise Exception.message('No links! Run getlinks() before parse()')

		for link in self.article links:
			d, t, author, raw_text = newspaper(link)
			self.dictify(self.dic, d, t, author, raw_text)

		return self.dic




class WorldCrunch(NewspaperScraper):

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
		if self.article_links = None:
			raise Exception.message('No links! Run getlinks() before parse()')

		for link in self.article links:
			d, t, author, raw_text = newspaper(link)
			self.dictify(self.dic, d, t, author, raw_text)

		return self.dic


class EurActiv(NewspaperScraper):
	
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
		if self.article_links = None:
			raise Exception.message("No links! Run 'getlinks()' before 'parse()'")

		for link in self.article links:
			d, t, author, raw_text = newspaper(link)
			self.dictify(self.dic, d, t, author, raw_text)

		return self.dic


class BBC(NewspaperScraper):
	base_url = 'http://www.bbc.com/news'

	def getlinks(self, name):
		split_name = '+'.join(name.split())
		for i in range(2,10):
			search_url = 'http://www.bbc.co.uk/search?q={}&page={}'.format(split_name, i)

		r = requests.get(search_url)
		soup = BeautifulSoup(r.text, 'lxml')

		results = soup.find_all("section", {"id":"search-content"})
		links = []
		
		for r in results[0].find_all("li"):
			if r.find("a")['href'] not in article_links:
				links.append(r.find("a")['href'])

		self.article_links.extend(links)
		
		return self.article_links  

	def parse(self):




class ProjectSyndicate(NewspaperScraper):
	base_url = ''

	def getlinks(self):

	def parse(self):