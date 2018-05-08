
import scrapy
from scrapy.spiders import CrawlSpider, Rule
import logging
import requests
import re
import time

from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings


def getLink(offset):
    offset = offset * 99
    url = 'https://zh.zalora.com.hk/_c/rpc?req=%7B%22method%22%3A%22Costa.ListProducts%22%2C%22params%22%3A%5B%7B%22limit%22%3A99%2C%22offset%22%3A{0}%2C%22dir%22%3A%22desc%22%2C%22sort%22%3A%22popularity%22%2C%22catalog_type%22%3A%22%22%2C%22category_id%22%3A%5Bnull%5D%2C%22url_key%22%3A%22%22%2C%22enable_visual_sort%22%3Atrue%7D%5D%7D&lang=zh'.format(offset)
    headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'}

    f = open(r'./cookie.txt', 'r')  # 打开所保存的cookies内容文件
    cookies = {}  # 初始化cookies字典变量
    for line in f.read().split(';'):  # 按照字符：进行划分读取
        # 其设置为1就会把字符串拆分成2份
        name, value = line.strip().split('=', 1)
        cookies[name] = value  # 为字典cookies添加内容

    try:
        data = requests.get(url, cookies=cookies, headers=headers).text
        links = re.findall(r'"link":"(.*?)"', data)
        skus = re.findall(r'"sku":"(.*?)"', data)
        if links:
            return links,skus
        else:
            return None
    except Exception as e:
        logging.exception("error")

class Item(scrapy.Item):
    sku = scrapy.Field()
    Title = scrapy.Field()
    Desc = scrapy.Field()

class ZaloraSpider(CrawlSpider):
    name = 'Zalora'
    download_delay = 3

    def start_requests(self):
        i = 1
        while True:
            Links,skus = getLink(i)
            if Links:
                for count, Link in enumerate(Links):
                    url = 'https://zh.zalora.com.hk/' + Link
                    yield scrapy.Request(url=url, callback=self.parse, meta={'sku': skus[count]})
            else:
                break
            i = i + 1
            time.sleep(20)

    def parse(self, response):
        item = Item()
        try:
            item['Title'] = response.xpath('normalize-space(//div[@class="product__title fsm"])').extract_first()
            item['Desc'] = response.xpath('normalize-space(//div[@id="productDesc"])').extract_first()
            item['sku'] = response.meta['sku']
            yield item
        except Exception as e:
            logging.exception("parse error")

def run():
    configure_logging()
    runner = CrawlerRunner(get_project_settings())
    d = runner.crawl(ZaloraSpider)
    d.addBoth(lambda _: reactor.stop())
    reactor.run() # the script will block here until the crawling is finished

if __name__ == '__main__':
    run()