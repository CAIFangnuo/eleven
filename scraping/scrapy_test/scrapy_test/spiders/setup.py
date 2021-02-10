import scrapy
from scrapy_test.items import ScrapyTestItem

class FirstSpider(scrapy.Spider):
    name = "Reviews"
    start_urls = [
        "https://www.airlinequality.com/airline-reviews/africa-world-airlines"
        ]

    def parse(self, response):
        item = ScrapyTestItem()
        item['headline'] = response.xpath('//*[@id="anchor728817"]/h2').extract()
        item['price'] = response.xpath('//*[@id="anchor728817"]/div/div[1]/text()[2]').extract()

        return item

        