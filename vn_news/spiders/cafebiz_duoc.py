import scrapy
from vn_news.items import DuocItem
from datetime import datetime
import re
class CafebizDuocSpider(scrapy.Spider):
	name = "cafebizduoc"
	allowed_domains = ["cafebiz.vn"]
	origin_doamin = 'https://cafebiz.vn'
	start_urls = [
		'https://cafebiz.vn/timelinetag/duoc-pham/1.htm', 
	]
	current_page = 1

	def parse(self, response):
		# Extract news article URLs from the page
		article_links = response.css('div.thread-right.fl h3 a::attr(href)').getall()
		# Follow each article URL and parse the article page
		for link in article_links:
			yield scrapy.Request(self.origin_doamin + link, callback=self.parse_article)
		# Next page
		print('current_page',self.current_page)
		self.current_page = int(response.url.split('/')[-1].split('.')[0])
		next_page = self.current_page + 1

		if next_page <= 10:
			next_page_link = response.url.replace(f"/{self.current_page}.htm", f"/{next_page}.htm")
			yield scrapy.Request(next_page_link, callback=self.parse)
	def formatString(self, text):
		if isinstance(text, list):  # Check if text is a list
			text = ' '.join(text)
		if text is not None :
			text = text.replace('\r\n','')
			text = text.replace('\n','')
			text = "".join(text.rstrip().lstrip())
		cleaned_text = re.sub(r'[^a-zA-Z0-9À-ỹ\s.,!?]', ' ', str(text))
		cleaned_string = re.sub(r'\s{2,}', ' ', cleaned_text)
		return cleaned_string
	def parse_article(self, response):
		print('start crawl detail article')
		# Extract information from the news article page
		title = response.css('h1.title::text').get()
		print('title',title)
		title = self.formatString(title)
		timeCreatePostOrigin = response.css('div.timeandcatdetail span.time::text').get()
		timeCreatePostOrigin = re.sub(r'\s{2,}', ' ', str(timeCreatePostOrigin))
		try :
			timeCreatePostOrigin  = timeCreatePostOrigin.strip()
			datetime_object = datetime.strptime(timeCreatePostOrigin, '%d/%m/%Y %H:%M %p')
			timeCreatePostOrigin = datetime_object.strftime('%Y/%m/%d')
		except Exception as e: 
				print('Do Not convert to datetime')
				print(e)
		author = response.css('p.p-author strong::text').get()
		author = author.replace('Theo','')
		author = re.sub(r'\s{2,}', ' ', str(author))
		summary = response.css('h2.sapo::text').get()
		summary = self.formatString(summary)
		summary_html = response.css('h2.sapo').get()
		content = response.css('div.detail-content p ::text').getall()
		content = self.formatString(content)
		content_html = response.css('div.detail-content').get()
		
		item = DuocItem(
			title=title,
			timeCreatePostOrigin=timeCreatePostOrigin,
			author = author,
			summary=summary,
			content=content,
			summary_html=summary_html,
			content_html = content_html,
			urlPageCrawl= 'cafebiz',
			url=response.url
		)
		if title == '' or title ==None or content =='' or content == None :
			yield None
		else :
			yield item


