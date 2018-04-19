
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

class mabelleSpider(CrawlSpider):
    name = 'mabelle'
    download_delay = 3

    allowed_domains = ['mabelle.com'
    ]

    start_urls = ['https://www.mabelle.com/eu/chs/products/,,,,,,,,,3000,1']

    rules = (
        Rule(
            LinkExtractor(restrict_xpaths=[
                "//div[@class='top-padding product-list']"],
            allow='/eu/chs/product/'),
            callback='parse_item'
        ),
    )

    def parse_item(self, response):
        try:
            title_zh = response.xpath('normalize-space(//*[@id="productName"])').extract_first()
            if response.xpath('normalize-space(//*[@id="mobile-wrapper"]/div[2]/div[2]/p[3])').extract_first():
                desc_zh = response.xpath('normalize-space(//*[@id="mobile-wrapper"]/div[2]/div[2]/p[3])').extract_first()
            elif response.xpath('normalize-space(//*[@id="mobile-wrapper"]/div[2]/div[2]/p[2])').extract_first():
                desc_zh = response.xpath('normalize-space(//*[@id="mobile-wrapper"]/div[2]/div[2]/p[2])').extract_first()
            else:
                desc_zh = []
            if title_zh:
                url_en = response.url.replace('eu/chs', 'eu/eng')
                request = scrapy.Request(url_en, callback=self.parse_item_en, meta={'Title': title_zh, 'Desc': desc_zh})
                yield request
        except Exception as e:
            logging.exception("parse error")

    def parse_item_en(self, response):
        item = EnZhItem()
        item['Title_zh'] = response.meta['Title']
        item['Desc_zh'] = response.meta['Desc']
        try:
            item['Title_en'] = response.xpath('normalize-space(//*[@id="productName"])').extract_first()
            if response.xpath('normalize-space(//*[@id="mobile-wrapper"]/div[2]/div[2]/p[3])').extract_first():
                item['Desc_en'] = response.xpath('normalize-space(//*[@id="mobile-wrapper"]/div[2]/div[2]/p[3])').extract_first()
            elif response.xpath('normalize-space(//*[@id="mobile-wrapper"]/div[2]/div[2]/p[2])').extract_first():
                item['Desc_en'] = response.xpath('normalize-space(//*[@id="mobile-wrapper"]/div[2]/div[2]/p[2])').extract_first()
            else:
                item['Desc_en'] = []
            yield item
        except Exception as e:
            logging.exception("parse error")


def run():
    configure_logging()
    runner = CrawlerRunner(get_project_settings())
    d = runner.crawl(mabelleSpider)
    d.addBoth(lambda _: reactor.stop())
    reactor.run() # the script will block here until the crawling is finished

if __name__ == '__main__':
    run()