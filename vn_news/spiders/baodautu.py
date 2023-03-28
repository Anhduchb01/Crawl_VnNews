import scrapy
from vn_news.items import VnNewsItem
from datetime import datetime

class BaodautuSpider(scrapy.Spider):
    name = "baodautu"
    allowed_domains = ["baodautu.vn"]
    origin_doamin = 'http://baodautu.vn'
    start_urls = [
        'https://baodautu.vn/dau-tu-d2/p1',  # đầu tư
        'https://baodautu.vn/doanh-nhan-d4/p1',  # doanh nhân
        'https://baodautu.vn/doanh-nghiep-d3/p1', # doanh nghiệp
        'https://baodautu.vn/tai-chinh-chung-khoan-d6/p1' , # tài chính- chứng khoán

    ]

    def parse(self, response):
        # Extract news article URLs from the page
        article_links = response.css('ul.list_news_home a.fs22.fbold::attr(href)').getall()
        # Follow each article URL and parse the article page
        for link in article_links:
            yield scrapy.Request(link, callback=self.parse_article)

        # Increment the page number and follow the next page
        current_page = int(response.url.split('/p')[-1])
        next_page = current_page + 1

        if next_page <= 10:
            next_page_link = response.url.replace(f"p{current_page}", f"p{next_page}")
            yield scrapy.Request(next_page_link, callback=self.parse)
    def formatString(self, text):
        text =  text.replace('"', '\"')  # escape double quotes
        text = text.replace("'", "\'")  # escape single quotes
        text = text.replace('/', '\/')  # escape forward slashes
        return text
    def parse_article(self, response):
        # Extract information from the news article page
        title = response.css('div.title-detail::text').get()
        try:
            title = " ".join(title.split())
            title = self.formatString(title)
        except:
            print('not split title')
        
        timeCreatePostOrigin = response.css('span.post-time::text').get()
        try:
            timeCreatePostOrigin = timeCreatePostOrigin.replace('-','')
            timeCreatePostOrigin = " ".join(timeCreatePostOrigin.split())
            datetime_object = datetime.strptime(timeCreatePostOrigin, '%d/%m/%Y %H:%M')
            timeCreatePostOrigin = datetime_object.strftime('%Y/%m/%d')
        except:
            print('Do Not convert to datetime')
        category = response.css('div.fs16.text-uppercase a::text').get()

        author = response.css('a.author.cl_green::text').get()
        author = author.replace('-','')
        author = " ".join(author.split())

        content_sum = response.css('div.sapo_detail::text').get()

        content_des = response.css('div#content_detail_news ::text').getall()
        content =str(content_sum)  + str(content_des)
        content = self.formatString(content)

        content_sum_html = response.css('div.sapo_detail').get()
        content_des_html = response.css('div#content_detail_news').get()
        content_html =str(content_sum_html)+str(content_des_html)
        # image_url = response.css('figure.detail__avatar img::attr(src)').get()
        
        
        # Create a CafefItem instance containing the information
        item = VnNewsItem(
            title=title,
            timeCreatePostOrigin=timeCreatePostOrigin,
            category=category,
            author=author,
            content=content,
            content_html= content_html,
            # image_url=image_url,
            urlPageCrawl= 'baodautu',
            url=response.url
        )
        
        # Return the item
        yield item

