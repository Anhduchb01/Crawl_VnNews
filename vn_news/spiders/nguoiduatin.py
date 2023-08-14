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
		title = response.css('h1.tmp-title-big::text').get()
		title = self.formatString(title)
		timeCreatePostOrigin = response.css('div.txt-datetime::text').get()
		try:
			date_portion = timeCreatePostOrigin.split(',')[1].split('|')[0].strip()
			datetime_object = datetime.strptime(date_portion, '%d/%m/%Y')
			timeCreatePostOrigin = datetime_object.strftime('%Y/%m/%d')
		except Exception as e: 
			print('Do Not convert to datetime')
			print(e)
		author = response.css('div.txt-name::text').get()
		author = self.formatString(author)

		summary = response.css('div.tmp-title-large::text').get()
		summary = self.formatString(summary)
		summary_html =  response.css('div.tmp-title-large').get()

		content = response.css('article.article-content p::text').getall()
		content = self.formatString(content)
		content_html = response.css('article.article-content').get()

		item = DuocItem(
			title=title,
			timeCreatePostOrigin=timeCreatePostOrigin,
			author = author,
			summary=summary,
			content=content,
			summary_html = summary_html,
			content_html = content_html,
			urlPageCrawl= 'nguoiduatin',
			url=response.url
		)
		if title == '' or title ==None or content =='' or content == None :
			yield None
		else :
			yield item
