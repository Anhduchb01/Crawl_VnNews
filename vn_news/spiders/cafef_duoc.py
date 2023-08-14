import scrapy
from vn_news.items import DuocItem
from datetime import datetime
import re
class CafefDuocSpider(scrapy.Spider):
	name = 'cafefduoc'
	allowed_domains = ['cafef.vn']
	origin_doamin = 'https://cafef.vn'
	start_urls = [
		'https://cafef.vn/duoc-pham/trang-1.html',  
	]
	current_page = 1

	def parse(self, response):
		# Extract news article URLs from the page
		article_links = response.css('div.knswli-right h3 a::attr(href)').getall()
		# Follow each article URL and parse the article page
		for link in article_links:
			yield scrapy.Request(self.origin_doamin + link, callback=self.parse_article)
		print('current page',self.current_page)
		next_page = self.current_page + 1
		if next_page <= 2:
			next_page_link = response.url.replace(f"{self.current_page}.html", f"{next_page}.html")
			self.current_page = next_page
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
		# Extract information from the news article page
		title = response.css('h1.title::text').get()
		title = self.formatString(title)
		timeCreatePostOrigin = response.css('span.pdate::text').get()
		if timeCreatePostOrigin is not None :
			timeCreatePostOrigin = "".join(timeCreatePostOrigin.rstrip().lstrip())
			try:
				datetime_object = datetime.strptime(timeCreatePostOrigin, '%d-%m-%Y - %H:%M %p')
				timeCreatePostOrigin = datetime_object.strftime('%Y/%m/%d')
			except Exception as e: 
				print('Do Not convert to datetime')
				print(e)
		
		author = response.css('p.author::text').get()
		
		summary = response.css('h2.sapo::text').get()
		summary = self.formatString(summary)
		summary_html = response.css('h2.sapo').get()

		content = response.css('div.detail-content.afcbc-body p ::text').getall()
		content = self.formatString(content)
		content_html = response.css('div.detail-content.afcbc-body').get()
		item = DuocItem(
			title=title,
			timeCreatePostOrigin=timeCreatePostOrigin,
			author = author,
			summary=summary,
			content=content,
			summary_html= summary_html,
			content_html = content_html,
			urlPageCrawl= 'cafef',
			url=response.url
		)
		if title == '' or title ==None or content =='' or content == None :
			yield None
		else :
			yield item
