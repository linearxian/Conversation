import scrapy


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = [
        'http://quotes.toscrape.com/page/1/',
    ]

    def parse(self, response):
        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').extract_first(),
                'author': quote.css('span small::text').extract_first(),
                'tags': quote.css('div.tags a.tag::text').extract(),
            }

        for a in response.css('li.next a'):
            yield response.follow(a, callback=self.parse)


class AuthorSpider(scrapy.Spider):
    name = 'author'

    start_urls = ['http://quotes.toscrape.com/']

    def parse(self, response):
        # follow links to author pages
        for href in response.css('.author + a::attr(href)'):
            yield response.follow(href, self.parse_author)

        # follow pagination links
        for href in response.css('li.next a::attr(href)'):
            yield response.follow(href, self.parse)

    def parse_author(self, response):
        def extract_with_css(query):
            return response.css(query).extract_first().strip()

        yield {
            'name': extract_with_css('h3.author-title::text'),
            'birthdate': extract_with_css('.author-born-date::text'),
            'bio': extract_with_css('.author-description::text'),
        }


class XboxSpider(scrapy.Spider):
    name = "Xbox"
    start_urls = [
        'https://www.microsoft.com/zh-hk/store/p/Fe/BZW2R4STVDNK?rtc=1',
    ]

    def parse(self, response):

        title = response.xpath('normalize-space(.//*[(@id = "page-title")])').extract_first()
        description = response.xpath('normalize-space(.//*[(@id = "product-description")])').extract_first()

        yield {
            'title': title,
            'description': description
        }


#if __name__ == "__main__":
 #   scrapy