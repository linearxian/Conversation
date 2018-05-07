import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import logging
import re

from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings


class dxoSpider(CrawlSpider):
    name = 'dxo'
    download_delay = 3

    start_urls = [
        'https://www.dxomark.com/cn/category/mobile-review/page/1/',
    ]

    rules = (
        Rule(
            LinkExtractor(restrict_xpaths=[
                # "//div[@class='col post-item']/div/a/@href"]),
                "//div[@class='col post-item']/div/a"]),
            callback='parse_item'
        ),
        Rule(
            LinkExtractor(restrict_xpaths=[
                # "//a[@class='next page-number']/@href"]),
                "//a[@class='next page-number']"]),
            callback='parse'
        )
    )

    def parse_item(self, response):
        namestr = response.url[-20:-1]
        namestr = namestr.replace('/', 'Slash')
        path_ps = "./Output/ps_" + namestr + "_zh.txt"
        path_lis = "./Output/lis_" + namestr + "_zh.txt"
        path_boxs = "./Output/boxs_" + namestr + "_zh.txt"
        out_ps = open(path_ps, "a")
        out_lis = open(path_lis, "a")
        out_boxs = open(path_boxs, "a")
        try:
            ps_list = response.selector.xpath('//p')
            for a in ps_list:
                temp = a.xpath('text()').extract()
                cat = ''.join(temp)
                if len(cat) > 10:
                    p = re.sub(' +', ' ', cat)
                    out_ps.write(p)
                    out_ps.write("\n")

            lis_list = response.selector.xpath('//li')
            for a in lis_list:
                temp = a.xpath('text()').extract()
                cat = ''.join(temp)
                if len(cat) > 10:
                    p = re.sub(' +', ' ', cat)
                    out_lis.write(p)
                    out_lis.write("\n")

            boxs_list = response.selector.xpath('//div[@class="box-text-inner"]')
            for a in boxs_list:
                temp = a.xpath('text()').extract()
                cat = ''.join(temp)
                if len(cat) > 10:
                    p = re.sub(' +', ' ', cat)
                    out_boxs.write(p)
                    out_boxs.write("\n")

            out_ps.close()
            out_lis.close()
            out_boxs.close()

            url_en = response.url.replace('dxomark.com/cn/', 'dxomark.com/')
            request = scrapy.Request(url_en, callback=self.parse_item_en)
            yield request
        except Exception as e:
            logging.exception("parse error")

    def parse_item_en(self, response):
        namestr = response.url[-20:-1]
        namestr = namestr.replace('/', 'Slash')
        path_ps = "./Output/ps_" + namestr + "_en.txt"
        path_lis = "./Output/lis_" + namestr + "_en.txt"
        path_boxs = "./Output/boxs_" + namestr + "_en.txt"
        en_out_ps = open(path_ps, "a")
        en_out_lis = open(path_lis, "a")
        en_out_boxs = open(path_boxs, "a")
        try:
            ps_list = response.selector.xpath('//p')
            for a in ps_list:
                temp = a.xpath('text()').extract()
                cat = ''.join(temp)
                if len(cat) > 10:
                    p = re.sub(' +', ' ', cat)
                    en_out_ps.write(p)
                    en_out_ps.write("\n")

            lis_list = response.selector.xpath('//li')
            for a in lis_list:
                temp = a.xpath('text()').extract()
                cat = ''.join(temp)
                if len(cat) > 10:
                    p = re.sub(' +', ' ', cat)
                    en_out_lis.write(p)
                    en_out_lis.write("\n")

            boxs_list = response.selector.xpath('//div[@class="box-text-inner"]')
            for a in boxs_list:
                temp = a.xpath('text()').extract()
                cat = ''.join(temp)
                if len(cat) > 10:
                    p = re.sub(' +', ' ', cat)
                    en_out_boxs.write(p)
                    en_out_boxs.write("\n")

            en_out_ps.close()
            en_out_lis.close()
            en_out_boxs.close()

        except Exception as e:
            logging.exception("parse error")

def run():
    configure_logging()
    runner = CrawlerRunner(get_project_settings())
    d = runner.crawl(dxoSpider)
    d.addBoth(lambda _: reactor.stop())
    reactor.run() # the script will block here until the crawling is finished

if __name__ == '__main__':
    run()