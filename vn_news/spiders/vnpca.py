import scrapy
from vn_news.items import NewsItem
from datetime import datetime
import re
class VnpcaSpider(scrapy.Spider):
	name = 'vnpca'
	allowed_domains = ['vnpca.org.vn']
	origin_doamin = 'https://vnpca.org.vn'
	start_urls = [
		'https://vnpca.org.vn/tin-tuc-su-kien', 
	]
	current_page = 0

	def parse(self, response):
		# Extract news article URLs from the page
		article_links = response.css('div.views-field-title > span >  a::attr(href)').getall()
		# Follow each article URL and parse the article page
		print('article_links',article_links)
		for link in article_links:
			if "/giay-phep-luu-hanh" not in str(link) :
				print('true')
				yield scrapy.Request(self.origin_doamin + link, callback=self.parse_article)

		# Increment the page number and follow the next page
		if self.current_page == 0:
			print('current_page = 0')
			self.current_page = 1
			next_page_link = response.url + f"?page={self.current_page}"
			
			yield scrapy.Request(next_page_link, callback=self.parse)
		else :
			print('current_page')
			print(self.current_page)
			print(response.url)
			print(response.url.split('?page=')[-1])
			self.current_page = int(response.url.split('?page=')[-1])
			next_page = self.current_page + 1
			if self.current_page <= 10:
				next_page_link = response.url.replace(f"?page={self.current_page}", f"?page={next_page}")
				self.current_page = next_page
				yield scrapy.Request(next_page_link, callback=self.parse)
	def formatString(self, text):
		cleaned_text = re.sub(r'[^a-zA-Z0-9À-ỹ\s.,!?]', '', text)
		return cleaned_text
	def parse_article(self, response):
		# Extract information from the news article page
		title = response.css('div.div-title::text').get()
		title = " ".join(title.split())
		title = self.formatString(title)
		timeCreatePostOrigin = response.css('div.div-ngay-tao > i::text').get()
		timeCreatePostOrigin = timeCreatePostOrigin.replace('[','')
		timeCreatePostOrigin = timeCreatePostOrigin.replace(']','')
		# try:
		#     datetime_object = datetime.strptime(timeCreatePostOrigin, '%d-%m-%Y - %I:%M %p ')
		#     timeCreatePostOrigin = datetime_object.strftime('%Y/%m/%d')
		# except:
		#     print('Do Not convert to datetime')
		summary = response.css('div.div-noi-dung.div-mo-ta-tin > p::text').get()

		content = response.css('div.noi-dung-tin > p::text').getall()
		content = ''.join(content).strip()
		content = self.formatString(content)
		# Create a CafefItem instance containing the information
		item = NewsItem(
			title=title,
			timeCreatePostOrigin=timeCreatePostOrigin,
			summary=summary,
			content=content,
			urlPageCrawl= 'vnpca',
			url=response.url
		)
		
		# Return the item
		yield item
