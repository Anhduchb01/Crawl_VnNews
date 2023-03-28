# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class VnNewsItem(scrapy.Item):
    title = scrapy.Field()
    timeCreatePostOrigin = scrapy.Field()
    category = scrapy.Field()
    author = scrapy.Field()
    content = scrapy.Field()
    content_html = scrapy.Field()
    image_url = scrapy.Field()
    urlPageCrawl = scrapy.Field()
    url = scrapy.Field()
class CafefItem(scrapy.Item):
    pass
