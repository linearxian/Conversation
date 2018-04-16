
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

class cosmeSpider(CrawlSpider):
    name = 'cosme'
    download_delay = 3

    start_urls = [
        'http://www.cosme-de.com/gb/brand/shop_by_brand.html',
    ]

    rules = (
        Rule(
            LinkExtractor(restrict_xpaths=[
                "//td[@class='product_name']"],
            allow='product_page.html'),
            callback='parse_item'
        ),
        Rule(
            LinkExtractor(restrict_xpaths=[
                "//td[@class='content_txt']"],
                allow='pg='),
            callback='parse'
        ),
        Rule(
            LinkExtractor(restrict_xpaths=[
                "//td[@class='content_txt']"],
                allow='brand_page.html'),
            callback='parse'
        ),
    )

    def parse_item(self, response):
        try:
            title_zh = response.xpath('normalize-space(//td[@itemprop="name"])').extract_first()
            desc_zh = response.xpath('normalize-space(//td[@itemprop="description"])').extract_first()
            if desc_zh:
                url_en = response.url.replace('/gb/', '/en/')
                request = scrapy.Request(url_en, callback=self.parse_item_en, meta={'Title': title_zh, 'Desc': desc_zh})
                yield request
        except Exception as e:
            logging.exception("parse error")

    def parse_item_en(self, response):
        item = EnZhItem()
        item['Title_zh'] = response.meta['Title']
        item['Desc_zh'] = response.meta['Desc']
        try:
            item['Title_en'] = response.xpath('normalize-space(//td[@itemprop="name"])').extract_first()
            item['Desc_en'] = response.xpath('normalize-space(//td[@itemprop="description"])').extract_first()
            yield item
        except Exception as e:
            logging.exception("parse error")

def run():
    configure_logging()
    runner = CrawlerRunner(get_project_settings())
    d = runner.crawl(cosmeSpider)
    d.addBoth(lambda _: reactor.stop())
    reactor.run() # the script will block here until the crawling is finished

if __name__ == '__main__':
    run()