# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SiteItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    domain = scrapy.Field()
    ip = scrapy.Field()
    port = scrapy.Field()
