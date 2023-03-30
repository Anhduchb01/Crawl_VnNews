import scrapy
from vn_news.items import VnNewsItem
from datetime import datetime

class CafebizSpider(scrapy.Spider):
    name = "cafebiz"
    allowed_domains = ["cafebiz.vn"]

    origin_doamin = 'http://cafebiz.vn'
    start_urls = [
        'https://cafebiz.vn/timelinelist/17647/1.htm',  # kinh doanh
        'https://cafebiz.vn/timelinelist/176114/1.htm',  # kinh tế vĩ mô
    ]

    def parse(self, response):
        # Extract news article URLs from the page
        article_links = response.css('a.cfbiznews_title.show-popup::attr(href)').getall()
        # Follow each article URL and parse the article page
        for link in article_links:
            yield scrapy.Request(self.origin_doamin + link, callback=self.parse_article)

        # Increment the page number and follow the next page
        current_page = int(response.url.split('/')[-1].split('.')[0])
        next_page = current_page + 1

        if next_page <= 10:
            next_page_link = response.url.replace(f"/{current_page}.htm", f"/{next_page}.htm")
            yield scrapy.Request(next_page_link, callback=self.parse)
    def formatString(self, text):
        text =  text.replace('"', '\"')  # escape double quotes
        text = text.replace("'", "\'")  # escape single quotes
        text = text.replace('/', '\/')  # escape forward slashes
        return text
    def parse_article(self, response):
        # Extract information from the news article page
        title = response.css('h1.title::text').get()
        try:
            title = " ".join(title.split())
            title = self.formatString(title)
        except:
            print('not split title')
        
        timeCreatePostOrigin = response.css('div.timeandcatdetail span.time::text').get()
        try :
            timeCreatePostOrigin  = timeCreatePostOrigin.strip()
            datetime_object = datetime.strptime(timeCreatePostOrigin, '%d/%m/%Y %H:%M %p')

            timeCreatePostOrigin = datetime_object.strftime('%Y/%m/%d')
        except:
            print('Do Not convert to datetime')
        category = response.css('div.timeandcatdetail a::text').get()

        author = response.css('p.p-author strong::text').get()
        author = author.replace('Theo','')
        author = " ".join(author.split())

        content_sum = response.css('h2.sapo::text').get()
        content_des = response.css('div.detail-content p ::text').getall()
        content =str(content_sum)  + str(content_des)
        content = self.formatString(content)

        content_sum_html = response.css('h2.h2.sapo').get()
        content_des_html = response.css('div.detail-content').get()
        content_html =str(content_sum_html)+str(content_des_html)
        image_url = response.css('div.detail-content img::attr(src)').get()
        responseURL = response.url
        
        # Create a CafefItem instance containing the information
        item = VnNewsItem(
            title=title,
            timeCreatePostOrigin=timeCreatePostOrigin,
            category=category,
            author=author,
            content=content,
            content_html= content_html,
            image_url=image_url,
            urlPageCrawl= 'cafebiz',
            url=response.url
        )
        
        # Return the item
        yield item

