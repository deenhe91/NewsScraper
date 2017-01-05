import scrapy


class QuotesSpider(scrapy.Spider):
    name = "news"

    # def start_requests(self):
    start_urls = [
            "http://www.bbc.co.uk/search?q=Mario+Draghi&sa_f=search-product&scope=#page=20",
            "https://euobserver.com/search?query=mario+draghi&sort=date&from=&to=&offset=",
            "https://euobserver.com/search?query=mario+draghi&sort=date&from=&to=&offset=30",
            "https://euobserver.com/search?query=mario+draghi&sort=date&from=&to=&offset=60",
            "https://euobserver.com/search?query=mario+draghi&sort=date&from=&to=&offset=90"]

        # for url in urls:
        #     yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = 'news-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)