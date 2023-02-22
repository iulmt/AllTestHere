import scrapy


class DemoSpider(scrapy.Spider):
    def parse(self, response, **kwargs):
        return {'a': 1}
