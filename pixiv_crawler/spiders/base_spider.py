"""Initial Base spider

This module uses a spider to log in to Pixiv
using a provided form data and then redirects to the user bookmarks.
"""
import base64
import scrapy
from scrapy.http import HtmlResponse
from scrapy.linkextractors import LinkExtractor
from scrapy_splash import SplashRequest, SplashJsonResponse

from .. import items

class BaseSpider(scrapy.Spider):
    """Initial spider to login to Pixiv page"""
    name = "login"

    start_urls = ['https://accounts.pixiv.net/login']
    bookmarks_page = 'https://www.pixiv.net/bookmark.php'

    # rules = {

    #     Rule(LinkExtractor(allow_domains='pixiv.net',
    #                        restrict_css=('div.display_editable_works a._work')),
    #                        process_request='processSplash')

    # }

    def parse(self, response):
        """Generates login form request"""

        return scrapy.FormRequest.from_response(
            response,
            formdata={"pixiv_id" : "lazeegutar@gmail.com", "password" : "2aseChuW"},
            callback=self.afterLogin
        )

    def afterLogin(self, response):
        """Check login validity

        Error case for login info.
        """
        # Login Case
        if b"error-msg-list__item" in response.body:
            self.logger.error("Login failed")
            return None

        self.logger.info("Login Successful!")
        return scrapy.Request(url=self.bookmarks_page, callback=self.parseBookmarks)

    def parseBookmarks(self, response):
        """Lua Script to wait until Splash renders element.
        
        Gets all artist work pages in current bookmarks.
        """

        wait_for_element = """
        function main(splash)
            splash:init_cookies(splash.args.cookies)
            assert(splash:go(splash.args.url))
            splash:wait(10)
            return {
                    cookies=splash:get_cookies(),
                    html=splash:html(),
                    url=splash:url(),
                    png=splash:png()}
        end
        """

        image_page_urls = response.css('div.display_editable_works a._work::attr(href)').extract()

        for images in image_page_urls:
            yield SplashRequest(response.url, self.getImage,
                                endpoint='execute',
                                

    def getImage(self, response):
        """Extract native image url from artist image page.
        
        Check if image url is an album
        Converts to item and insert into pipeline.
        """

        from scrapy.shell import inspect_response
        inspect_response(response, self)

        png_bytes = base64.b64decode(response.data['png'])
        with open('debug.png', 'wb') as out_file:
           out_file.write(png_bytes)

        item = items.PixivCrawlerItem()
        item['image_urls'] = [response.xpath('//div[@role="presentation"]//a/@href').extract_first()]
        item['referer'] = [response.url]
        return item

    # def _requests_to_follow(self, response):
    #     """Overridden to process SplashJsonResponse"""

    #     if not isinstance(response, HtmlResponse) and not isinstance(response, SplashJsonResponse):
    #         return
    #     seen = set()
    #     for n, rule in enumerate(self._rules):
    #         links = [lnk for lnk in rule.link_extractor.extract_links(response)
    #                  if lnk not in seen]
    #         if links and rule.process_links:
    #             links = rule.process_links(links)
    #         for link in links:
    #             seen.add(link)
    #             r = self._build_request(n, link)
    #             yield rule.process_request(r)
