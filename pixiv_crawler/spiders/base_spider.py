"""Initial Base spider

This module uses a spider to log in to Pixiv
using a provided form data and then redirects to the user bookmarks.
"""
import base64
import scrapy
from scrapy_splash import SplashRequest, SplashJsonResponse

from .. import items

class BaseSpider(scrapy.Spider):
    """Initial spider to login to Pixiv page"""
    name = "login"
    allow_domains = ['pixiv.net']

    start_urls = ['https://accounts.pixiv.net/login']

    def parse(self, response):
        """Function called before crawling"""

         return scrapy.FormRequest.from_response(
            response,
            formdata={"pixiv_id" : "lazeegutar@gmail.com", "password" : "2aseChuW"},
            callback=self.afterLogin
        )
    
    def login(self, response):
        """Generates login form request"""
       

    def afterLogin(self, response):
        """Check login validity

        Error case for login info.
        """
        # Login Case
        if b"error-msg-list__item" in response.body:
            self.logger.error("Login failed")
            return None

        self.logger.info("Login Successful!")
        return scrapy.Request(url=self.bookmarks_page)

    def processSplash(self, request):
        """Lua Script to wait until Splash renders element."""

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

        return SplashRequest(request.url, self.getImage,
                             endpoint='execute',
                             cache_args=['lua_source'],
                             args={
                                 'css' : 'div.css-4f40ux',
                                 'lua_source' : wait_for_element
                                 }
                            )


    def getImage(self, response):
        """Extract native image url from artist image page.
        
        Check if image url is an album
        Converts to item and insert into pipeline.
        """
        png_bytes = base64.b64decode(response.data['png'])
        with open('debug.png', 'wb') as outFile:
           outFile.write(png_bytes)

        item = items.PixivCrawlerItem()
        item['image_urls'] = [response.xpath('//div[@role="presentation"]//a/@href').extract_first()]
        item['referer'] = [response.url]
        return item

    def _requests_to_follow(self, response):
        """Overridden to process SplashJsonResponse"""

        if not isinstance(response, HtmlResponse) and not isinstance(response, SplashJsonResponse):
            return
        seen = set()
        for n, rule in enumerate(self._rules):
            links = [lnk for lnk in rule.link_extractor.extract_links(response)
                     if lnk not in seen]
            if links and rule.process_links:
                links = rule.process_links(links)
            for link in links:
                seen.add(link)
                r = self._build_request(n, link)
                yield rule.process_request(r)
