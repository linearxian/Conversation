
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import logging

from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings


class EnZhItem(scrapy.Item):
    Title_en = scrapy.Field()
    Desc_en = scrapy.Field()
    Title_zh = scrapy.Field()
    Desc_zh = scrapy.Field()

class ikeaSpider(CrawlSpider):
    name = 'ikea'
    download_delay = 3

    start_urls = [
        'https://www.ikea.cn/cn/zh/catalog/allproducts/',
    ]

    rules = (
        Rule(LinkExtractor(allow='/catalog/products/'),
            callback='parse_item'
        ),
        Rule(
            LinkExtractor(allow='/catalog/categories/departments/'),
            callback='parse'
        )
    )

    def parse_item(self, response):
        title_zh = []
        desc_zh = []
        try:
            title_1 = response.xpath('normalize-space(//span[@id="name"])').extract_first()
            title_zh.append(title_1)
            title_2 = response.xpath('normalize-space(//span[@id="type"])').extract_first()
            title_zh.append(title_2)

            desc_1 = response.xpath('normalize-space(//div[@id="salesArg"])').extract_first()
            desc_zh.append(desc_1)
            desc_2 = response.xpath('normalize-space(//div[@id="goodToKnow"])').extract_first()
            desc_zh.append(desc_2)
            desc_3 = response.xpath('normalize-space(//div[@id="soldSeparately"])').extract_first()
            desc_zh.append(desc_3)
            desc_4 = response.xpath('normalize-space(//div[@id="careInst"])').extract_first()
            desc_zh.append(desc_4)
            desc_5 = response.xpath('normalize-space(//div[@id="custMaterials"])').extract_first()
            desc_zh.append(desc_5)
            if desc_zh:
                url_en = response.url.replace('/cn/zh/', '/cn/en/')
                request = scrapy.Request(url_en, callback=self.parse_item_en, meta={'Title': title_zh, 'Desc': desc_zh})
                yield request
        except Exception as e:
            logging.exception("parse error")

    def parse_item_en(self, response):
        item = EnZhItem()
        item['Title_zh'] = response.meta['Title']
        item['Desc_zh'] = response.meta['Desc']
        title_en = []
        desc_en = []
        try:
            title_1 = response.xpath('normalize-space(//span[@id="name"])').extract_first()
            title_en.append(title_1)
            title_2 = response.xpath('normalize-space(//span[@id="type"])').extract_first()
            title_en.append(title_2)

            desc_1 = response.xpath('normalize-space(//div[@id="salesArg"])').extract_first()
            desc_en.append(desc_1)
            desc_2 = response.xpath('normalize-space(//div[@id="goodToKnow"])').extract_first()
            desc_en.append(desc_2)
            desc_3 = response.xpath('normalize-space(//div[@id="soldSeparately"])').extract_first()
            desc_en.append(desc_3)
            desc_4 = response.xpath('normalize-space(//div[@id="careInst"])').extract_first()
            desc_en.append(desc_4)
            desc_5 = response.xpath('normalize-space(//div[@id="custMaterials"])').extract_first()
            desc_en.append(desc_5)
            item['Title_en'] = title_en
            item['Desc_en'] = desc_en
            yield item
        except Exception as e:
            logging.exception("parse error")

def run():
    configure_logging()
    runner = CrawlerRunner(get_project_settings())
    d = runner.crawl(ikeaSpider)
    d.addBoth(lambda _: reactor.stop())
    reactor.run() # the script will block here until the crawling is finished

if __name__ == '__main__':
    run()