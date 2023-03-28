import scrapy
from vn_news.items import VnNewsItem
from datetime import datetime
class CafefSpider(scrapy.Spider):
    name = 'cafef'
    allowed_domains = ['cafef.vn']
    origin_doamin = 'https://cafef.vn'
    start_urls = [
        'https://cafef.vn/timelinelist/18836/1.chn',  # doanh nghiệp
        'https://cafef.vn/timelinelist/18831/1.chn',  # chứng khoán
    ]

    def parse(self, response):
        # Extract news article URLs from the page
        article_links = response.css('div.tlitem.box-category-item  h3  a::attr(href)').getall()
        # Follow each article URL and parse the article page
        for link in article_links:
            yield scrapy.Request(self.origin_doamin + link, callback=self.parse_article)

        # Increment the page number and follow the next page
        current_page = int(response.url.split('/')[-1].split('.')[0])
        next_page = current_page + 1
        if next_page <= 2:
            next_page_link = response.url.replace(f"/{current_page}.chn", f"/{next_page}.chn")
            yield scrapy.Request(next_page_link, callback=self.parse)
    def formatString(self, text):
        text =  text.replace('"', '\"')  # escape double quotes
        text = text.replace("'", "\'")  # escape single quotes
        text = text.replace('/', '\/')  # escape forward slashes
        return text
    def parse_article(self, response):
        # Extract information from the news article page
        title = response.css('h1.title::text').get()
        title = " ".join(title.split())
        title = self.formatString(title)
        timeCreatePostOrigin = response.css('span.pdate::text').get()
        try:
            datetime_object = datetime.strptime(timeCreatePostOrigin, '%d-%m-%Y - %I:%M %p ')
            timeCreatePostOrigin = datetime_object.strftime('%Y/%m/%d')
        except:
            print('Do Not convert to datetime')
        category = response.css('a.category-page__name.cat::text').get()
        author = response.css('p.author::text').get()
        content = response.css('div.detail-content.afcbc-body p::text').getall()
        content = ''.join(content).strip()
        content = self.formatString(content)
        content_title = response.css('h2.sapo').get()
        content_des = response.css('div.contentdetail').get()
        content_html = content_title+content_des
        image_url = response.css('div.media img::attr(src)').get()
        
        
        # Create a CafefItem instance containing the information
        item = VnNewsItem(
            title=title,
            timeCreatePostOrigin=timeCreatePostOrigin,
            category=category,
            author=author,
            content=content,
            content_html= content_html,
            image_url=image_url,
            urlPageCrawl= 'cafef',
            url=response.url
        )
        
        # Return the item
        yield item
