import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from landbank.items import Article


class landbankSpider(scrapy.Spider):
    name = 'landbank'
    start_urls = ['https://www.landbank.com/news']

    def parse(self, response):
        links = response.xpath('//div[@class="card-body text-center"]/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@aria-label="Next »"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h2/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="p-0"]/text()[2]').get()
        if date:
            date = " ".join(date.split())

        content = response.xpath('//div[@class="body mb-4"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content[1:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
