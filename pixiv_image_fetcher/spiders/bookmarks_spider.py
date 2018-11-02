"""Initial Base spider

This module uses a spider to log in to Pixiv
using a provided form data and then redirects to the user bookmarks.
"""

import re
import scrapy
# from scrapy.http import HtmlResponse
# from scrapy.linkextractors import LinkExtractor

from .. import items

class BookmarksSpider(scrapy.Spider):
    """Initial spider to login to Pixiv page"""
    name = "login"

    allowed_domains = ['pixiv.net', 'i.pximg.net']

    start_urls = ['https://accounts.pixiv.net/login']
    bookmarks_page = 'https://www.pixiv.net/bookmark.php'

    # User Input
    pixiv_id = 'lazeegutar@gmail.com'
    password = '2aseChuW'
    max_page_number = 1

    # Class Variables
    user_id = ''
    illust_pattern = re.compile(r'member.+?\d+')
    # orig_image_pattern = re.compile(r'"original":"(.*?)"')
    orig_image_pattern = re.compile(r'(c.*?master)(.*?)(_m.*?g)')
    selector_pattern = re.compile(r'class="(.*?)".*?data-src="(.*?)".*? \
                                  data-id="(\d+)".*?data-user-id="(\d+)"')

    # rules = {

    #     Rule(LinkExtractor(allow_domains='pixiv.net',
    #                        restrict_css=('div.display_editable_works a._work')),
    #                        process_request='processSplash')

    # }

    def parse(self, response):
        """Generates login form request"""

        return scrapy.FormRequest.from_response(
            response,
            formdata={'pixiv_id' : self.pixiv_id, 'password' : self.password},
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

        user_id_pattern = re.compile(r'pixiv\.user\.id = "(\d+?)"')
        self.user_id = response.xpath('//head/script[contains(., "pixiv.user.id = ")]/text()') \
                                 .re(user_id_pattern)[0]

        self.logger.info("Login Successful!")
        return scrapy.Request(url=self.bookmarks_page, callback=self.parseBookmarks)

    def parseBookmarks(self, response):
        """Gets all artist illustrations and artist info in current bookmark page.

        Case if artist illustration is an album and contains multiple images.
        Recursively calls next page.
        """
        illust_selectors = response.css('div.display_editable_works a._work')
        item = items.BookmarksImage()
        item['user_id'] = self.user_id

        # artist_ids = response.xpath('//div[@class="display_editable_works"]//a/@data-user_id') \
        #                      .extract()

        for illust_selector in illust_selectors:
            referer = response.urljoin(illust_selector.xpath('@href').extract_first())
            thumbnail_image_url = illust_selector.xpath('div/img/@data-src').extract_first()
            orig_image_url = re.sub(self.orig_image_pattern, r'img-original\g<2>',
                                    thumbnail_image_url)
            illust_id = illust_selector.xpath('div/img/@data-id').extract_first()
            artist_id = illust_selector.xpath('div/img/@data-user-id').extract_first()
            item['image_urls'] = [orig_image_url]
            item['illust_id'] = illust_id
            item['artist_id'] = artist_id
            item['referer'] = referer

            if 'multiple' in illust_selector.extract():
                num_of_images = int(illust_selector.xpath('div/span/text()').extract_first())
                for image_num in range(1, num_of_images):
                    #todo last digit manipulation bug
                    index = orig_image_url.rfind('p') + 1
                    orig_image_url = orig_image_url[:index] + str(image_num)
                    item['image_urls'].append(orig_image_url)
            yield item

        next_page = response.xpath('//span[@class="next"]/a/@href').extract_first()
        index = next_page.rfind('=') + 1
        next_page_number = int(next_page[index :])

        if next_page is not None and next_page_number <= self.max_page_number:
            yield response.follow(url=next_page, callback=self.parseBookmarks)

    # def parseAlbum(self, response):
    #     """Obtain all image urls in current album."""

    #     album_images = response.css('section.manga a::attr(href)').extract()
    #     for count, image_url in enumerate(album_images):
    #         yield response.follow(url=image_url, callback=self.getImage,
    #                               meta={
    #                                   'image_num' : count + 1,
    #                                   'artist_id' : response.meta['artist_id'],
    #                                   'illust_id' : response.meta['illust_id'],
    #                                   'album' : True,
    #                                   }
    #                              )

    # def getImage(self, response):
    #     """Extract native image url from artist image page.

    #     Case if response has is an album
    #     """

    #     item = items.BookmarksImage()
    #     item['user_id'] = [self.user_id]
    #     item['artist_id'] = [response.meta['artist_id']]
    #     item['illust_id'] = [response.meta['illust_id']]
    #     item['referer'] = [response.url]

    #     album = response.meta.get('album')

    #     if album:
    #         orig_image_url = response.xpath('//img/@src').extract_first()
    #         item['image_num'] = [response.meta['image_num']]
    #     else:
    #         orig_image_selector = response.xpath('//head/script[contains(., "urls")]/text()')
    #         orig_image_str = orig_image_selector.re(self.orig_image_pattern)[0]
    #         orig_image_url = orig_image_str.replace('\\', '')

    #     item['image_urls'] = [orig_image_url]
    #     yield item
