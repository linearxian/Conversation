
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import logging

from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

import requests
from lxml import html
import time


def getLink(pageNum):
    pageNum = pageNum + 1
    try:
        with requests.session() as MySession:
            url = 'https://www.farfetch.com/cn/shopping/women/clothing-1/items.aspx?page={0}&view=90'.format(pageNum)
            response = MySession.get(url)
            root = html.fromstring(response.content)
            links = root.xpath("//a[@itemprop='url']/@href")
            return links
    except Exception as e:
        logging.exception("network error")
        return None

class EnZhItem(scrapy.Item):
    Title_en = scrapy.Field()
    Desc_en = scrapy.Field()
    Title_zh = scrapy.Field()
    Desc_zh = scrapy.Field()

class farfetchSpider(CrawlSpider):
    name = 'farfetch'
    download_delay = 3

    def start_requests(self):
        for i in range(1012):
            links = getLink(i)
            if links:
                for link in links:
                    url = 'https://www.farfetch.com' + link
                    yield scrapy.Request(url=url, callback=self.parse)
            time.sleep(5)

    def parse(self, response):
        try:
            title_zh = response.xpath("normalize-space(//p[@data-tstid='cardInfo-description'])").extract_first()
            desc_zh = response.xpath("normalize-space(//p[@data-tstid='fullDescription'])").extract_first()
            if desc_zh:
                url_en = response.url.replace('/cn/', '/hk/')
                request = scrapy.Request(url_en, callback=self.parse_item_en, meta={'Title': title_zh, 'Desc': desc_zh})
                yield request
        except Exception as e:
            logging.exception("parse error")

    def parse_item_en(self, response):
        item = EnZhItem()
        item['Title_zh'] = response.meta['Title']
        item['Desc_zh'] = response.meta['Desc']
        try:
            item['Title_en'] = response.xpath("normalize-space(//p[@data-tstid='cardInfo-description'])").extract_first()
            item['Desc_en'] = response.xpath("normalize-space(//p[@data-tstid='fullDescription'])").extract_first()
            yield item
        except Exception as e:
            logging.exception("parse error")

def run():
    configure_logging()
    runner = CrawlerRunner(get_project_settings())
    d = runner.crawl(farfetchSpider)
    d.addBoth(lambda _: reactor.stop())
    reactor.run() # the script will block here until the crawling is finished

if __name__ == '__main__':
    run()