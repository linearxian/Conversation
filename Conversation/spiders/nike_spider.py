import scrapy
from scrapy.spiders import CrawlSpider, Rule
import logging
import time

from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

from selenium import webdriver
from bs4 import BeautifulSoup

def getLink(seed):
    driver=webdriver.Chrome()
    try:
        driver.get(seed)

        def execute_times(times):
            for i in range(times + 1):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(5)

        execute_times(6)
    except Exception as e:
        logging.exception("network error")
        return None

    html = driver.page_source
    soup1 = BeautifulSoup(html,'lxml')
    products = soup1.select('a.product_list_name')
    products_hrefs=[]
    for product in products:
        products_hrefs.append('https://www.nike.com.hk'+ product.get('href'))

    hrefs_seen = set()  # holds lines already seen
    for href in products_hrefs:
        if href not in hrefs_seen:  # not a duplicate
            hrefs_seen.add(href)

    if hrefs_seen:
        return hrefs_seen
    else:
        return None

class EnZhItem(scrapy.Item):
    li_en = scrapy.Field()
    p_en = scrapy.Field()
    li_zh = scrapy.Field()
    p_zh = scrapy.Field()

class NikeSpider(CrawlSpider):
    name = 'nike'
    download_delay = 3

    def start_requests(self):
        seed = "https://www.nike.com.hk/man/shoe/list.htm?locale=zh-hk"
        word = 'detail.htm?'
        links = getLink(seed)
        if links:
            for link in links:
                if word in link:
                    yield scrapy.Request(url=link, callback=self.parse)

    def parse(self, response):
        try: # UC!!!!
            li = response.xpath('//div[@class="mini-description"]/li/text()').extract()
            p = []
            list = response.selector.xpath('//div[@class="mini-description"]/p')
            for a in list:
                temp = a.xpath('normalize-space()').extract_first()
                p.append(temp)
            url_en = response.url.replace('detail.htm?', 'detail.htm?locale=en-gb&')
            request = scrapy.Request(url_en, callback=self.parse_en, meta={'li': li, 'p': p})
            yield request
        except Exception as e:
            logging.exception("parse error")

    def parse_en(self, response):
        item = EnZhItem()
        item['li_zh'] = response.meta['li']
        item['p_zh'] = response.meta['p']
        try:
            li = response.xpath('//div[@class="mini-description"]/li/text()').extract()
            p = []
            list = response.selector.xpath('//div[@class="mini-description"]/p')
            for a in list:
                temp = a.xpath('normalize-space()').extract_first()
                p.append(temp)
            item['li_en'] = li
            item['p_en'] = p
            yield item
        except Exception as e:
            logging.exception("parse error")


def run():
    configure_logging()
    runner = CrawlerRunner(get_project_settings())
    d = runner.crawl(NikeSpider)
    d.addBoth(lambda _: reactor.stop())
    reactor.run() # the script will block here until the crawling is finished

if __name__ == '__main__':
    run()