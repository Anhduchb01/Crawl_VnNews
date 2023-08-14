import scrapy
from vn_news.items import DuocItem
from datetime import datetime
import re
class ThanhNienSpider(scrapy.Spider):
	name = "thanhnien"
	allowed_domains = ["thanhnien.vn"]
	origin_doamin = 'https://thanhnien.vn'
	start_urls = [
		'https://thanhnien.vn/timelinetag/duoc-pham/1.htm', 
	]
	current_page = 1

	def parse(self, response):
		# Extract news article URLs from the page
		article_links = response.css('h3.box-title-text a::attr(href)').getall()
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
		return cleaned_string
	def parse_article(self, response):
		print('start crawl detail article')
		# Extract information from the news article page
		title = response.css('h1.detail-title span::text').get()
		print('title',title)
		title = self.formatString(title)
		timeCreatePostOrigin = response.css('div.detail-time div::text').get()
		timeCreatePostOrigin = re.sub(r'\s{2,}', ' ', str(timeCreatePostOrigin))
		timeCreatePostOrigin = "".join(timeCreatePostOrigin.rstrip().lstrip())
		try :
			date_portion, time_portion = timeCreatePostOrigin.split(' ', 1)
			datetime_object = datetime.strptime(date_portion, '%d/%m/%Y')
			timeCreatePostOrigin = datetime_object.strftime('%Y/%m/%d')
		except Exception as e: 
				print('Do Not convert to datetime')
				print(e)
		author = response.css('div.author-info-top a::text').get()
		author = re.sub(r'\s{2,}', ' ', str(author))
		
		summary = response.css('h2.detail-sapo::text').get()
		summary = self.formatString(summary)
		summary_html  = response.css('h2.detail-sapo').get()

		content = response.css('div.detail-cmain p ::text').getall()
		content = self.formatString(content)
		content_html = response.css('div.detail-cmain').get()
		item = DuocItem(
			title=title,
			timeCreatePostOrigin=timeCreatePostOrigin,
			author = author,
			summary=summary,
			content=content,
			summary_html = summary_html,
			content_html = content_html,
			urlPageCrawl= 'thanhnien',
			url=response.url
		)
		if title == '' or title ==None or content =='' or content == None :
			yield None
		else :
			yield item

