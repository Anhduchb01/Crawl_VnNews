import scrapy
from vn_news.items import DuocItem
from datetime import datetime
import re
import requests
class NguoiDuaTinSpider(scrapy.Spider):
	name = 'nguoiduatin'
	allowed_domains = ['nguoiduatin.vn']
	origin_doamin = 'https://www.nguoiduatin.vn'
	start_urls = ['https://www.nguoiduatin.vn/tag-ajax/34687/layout/desktop/page/1']
	current_page = 1

	def parse(self, response):
		data = response.json().get('html', '')
		if data:
			selector = scrapy.selector.Selector(text=data)
			for link in selector.css('a.image-news'):
				href = link.attrib['href']
				print(href)
				yield scrapy.Request(self.origin_doamin + href, callback=self.parse_article)
			print('current_page',self.current_page)
			next_page = self.current_page +1
			next_page_link = response.url.replace(f"page/{self.current_page}",f"page/{next_page}")
			self.current_page = next_page
			yield scrapy.Request(next_page_link, callback=self.parse)

	def formatString(self, text):
		cleaned_text = re.sub(r'[^a-zA-Z0-9À-ỹ\s.,!?]', '', text)
		return cleaned_text
	def parse_article(self, response):
		# Extract information from the news article page
		title = response.css('h1.tmp-title-big::text').get()
		title = " ".join(title.split())
		title = self.formatString(title)
		timeCreatePostOrigin = response.css('div.txt-datetime::text').get()
		author = response.css('div.txt-name::text').get()
		# try:
		#     datetime_object = datetime.strptime(timeCreatePostOrigin, '%d-%m-%Y - %I:%M %p ')
		#     timeCreatePostOrigin = datetime_object.strftime('%Y/%m/%d')
		# except:
		#     print('Do Not convert to datetime')
		summary = response.css('div.tmp-title-large::text').get()

		content = response.css('article.article-content p::text').getall()
		content = ''.join(content).strip()
		content = self.formatString(content)

		item = DuocItem(
			title=title,
			timeCreatePostOrigin=timeCreatePostOrigin,
			author = author,
			summary=summary,
			content=content,
			urlPageCrawl= 'nguoiduatin',
			url=response.url
		)
		yield item
