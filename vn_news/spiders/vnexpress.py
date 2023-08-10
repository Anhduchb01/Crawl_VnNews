import scrapy
from vn_news.items import DuocItem
from datetime import datetime
import re
class VnexpressSpider(scrapy.Spider):
	name = 'vnexpress'
	allowed_domains = ['vnexpress.net']
	origin_doamin = 'https://vnexpress.net/'
	start_urls = [
		'https://vnexpress.net/tag/duoc-pham-756653',
	]
	current_page = 1

	def parse(self, response):
		# Extract news article URLs from the page
		article_links = response.css('h2.title-news a::attr(href)').getall()
		# Follow each article URL and parse the article page
		for link in article_links:
			yield scrapy.Request(link, callback=self.parse_article)

		# Increment the page number and follow the next page
		if self.current_page == 1:
			self.current_page +=1
			next_page_link = response.url + f"-p{self.current_page}"
			yield scrapy.Request(next_page_link, callback=self.parse)
		else: 
			self.current_page = int(response.url.split('-p')[-1])
			next_page = self.current_page + 1
			if next_page <= 5:
				next_page_link = response.url.replace(f"-p{self.current_page}", f"-p{next_page}")
				self.current_page = next_page
				yield scrapy.Request(next_page_link, callback=self.parse)
	def formatString(self, text):
		cleaned_text = re.sub(r'[^a-zA-Z0-9À-ỹ\s.,!?]', ' ', text)
		return cleaned_text
	def parse_article(self, response):
		# Extract information from the news article page
		title = response.css('h1.title-detail::text').get()
		title = self.formatString(title)
		timeCreatePostOrigin = response.css('span.date::text').get()
		# try:
		#     datetime_object = datetime.strptime(timeCreatePostOrigin, '%d-%m-%Y - %I:%M %p ')
		#     timeCreatePostOrigin = datetime_object.strftime('%Y/%m/%d')
		# except:
		#     print('Do Not convert to datetime')
		author = response.css('p.Normal[align="right"] strong::text').get()
		if author == None or author == "":
			author = response.css('p.Normal[style="text-align:right;"] strong::text').get()
			if author == None or author == "":
				author = response.css('p.Normal[style="text-align:right;"] em::text').get()
				if author == None or author == "":
					author = response.css('p.Normal[style="text-align:right;"]').get()
		# try:
		#     datetime_object = datetime.strptime(timeCreatePostOrigin, '%d-%m-%Y - %I:%M %p ')
		#     timeCreatePostOrigin = datetime_object.strftime('%Y/%m/%d')
		# except:
		#     print('Do Not convert to datetime')
		summary = response.css('div.sidebar-1 > p.description::text').get()

		content = response.css('article.fck_detail p::text').getall()
		content = ''.join(content).strip()
		content = self.formatString(content)
		
		
		# Create a CafefItem instance containing the information
		item = DuocItem(
			title=title,
			timeCreatePostOrigin=timeCreatePostOrigin,
			author = author,
			summary=summary,
			content=content,
			urlPageCrawl= 'vnexpress',
			url=response.url
		)
		
		# Return the item
		yield item
