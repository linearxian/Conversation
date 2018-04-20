# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
import re
import requests
import time

from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings


class PIDItem(scrapy.Item):
    PID = scrapy.Field()

class JDConversationSpider(CrawlSpider):
    name = "JDConversation"
    download_delay = 3
    start_urls = [
        'http://list.jd.com/list.html?cat=670,671,672',
    ]

    def parse(self,response):
        if response.status==200:
            try:
                all_goods = response.xpath("//div[@id='plist']/ul/li/div")
                for goods in all_goods:
                    item = PIDItem()
                    pid = goods.xpath("@data-sku").extract()
                    if pid:
                            item['PID'] = pid[0]
                            yield item
            except Exception:
                print('--------------ERROR--------------')

            # find next page
            time.sleep(5)
            next_page = response.xpath('//a[@class="pn-next"]/@href').extract()
            if next_page:
                next_page = "https://list.jd.com" + next_page[0]
                print('--------------Finding next page--------------')
                yield scrapy.Request(next_page, callback=self.parse)
            else:
                print('--------------There is no more page!--------------')

def run():
    configure_logging()
    runner = CrawlerRunner(get_project_settings())
    d = runner.crawl(JDConversationSpider)
    d.addBoth(lambda _: reactor.stop())
    reactor.run() # the script will block here until the crawling is finished

if __name__ == '__main__':
    run()