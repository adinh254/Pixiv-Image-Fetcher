"""Initial Base spider

This module uses a spider to log in to Pixiv
using a provided form data and then redirects to the user bookmarks.
"""

import re
import os

import scrapy

from scrapy.spidermiddlewares.httperror import HttpError

from .. import items

class BookmarksSpider(scrapy.Spider):
    """Initial spider to login to Pixiv page"""
    name = "login"

    allowed_domains = ['pixiv.net', 'i.pximg.net']

    start_urls = ['https://accounts.pixiv.net/login']
    bookmarks_page = 'https://www.pixiv.net/bookmark.php?rest=show'

    # User Input
    pixiv_id = 'decayingapple@gmail.com'
    password = '1L1KEceRE4l'
    starting_page = 14
    last_page = 14

    # Class Variables
    user_id = ''
    orig_image_pattern = re.compile(r'(c.*?master)(.*?)(_m.*?)(.jpg)')

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
        if self.starting_page:
            self.bookmarks_page += '&p=%s' % str(self.starting_page)
        return scrapy.Request(url=self.bookmarks_page, callback=self.parseBookmarks)

    def parseBookmarks(self, response):
        """Gets all artist illustrations and artist info in current bookmark page.

        Case if artist illustration is an album and contains multiple images.
        Recursively calls next page.
        """

        from scrapy.shell import inspect_response
        inspect_response(response, self)

        # Filters out ugoiras
        illust_selectors = response.xpath(r'//div[@class="display_editable_works"]'
                                          r'//a[contains(concat(" ", @class, " "), " _work ")'
                                          r'and not(contains(concat(" ", @class, " "), '
                                          r'" ugoku-illust "))]')
        for illust_selector in illust_selectors:
            referer = response.urljoin(illust_selector.xpath('./@href').extract_first())
            thumbnail_image_url = illust_selector.xpath('./div/img/@data-src').extract_first()
            orig_image_url = re.sub(self.orig_image_pattern, r'img-original\g<2>\g<4>',
                                    thumbnail_image_url)
            illust_id = illust_selector.xpath('./div/img/@data-id').extract_first()
            artist_id = illust_selector.xpath('./div/img/@data-user-id').extract_first()
            num_of_images = illust_selector.xpath('./div/span/text()').extract_first()
            if artist_id != '0':
                item = items.BookmarksImage()
                item['user_id'] = self.user_id
                item['illust_id'] = illust_id
                item['artist_id'] = artist_id
                item['referer'] = referer

                yield scrapy.Request(url=orig_image_url,
                                     callback=self.getImage,
                                     errback=self.retryFormat,
                                     headers={
                                         'referer': referer,
                                     },
                                     meta={
                                         'item' : item,
                                         'num_of_images' : num_of_images,
                                     })
            else:
                self.logger.warning('Illustration %s has been deleted.', illust_id)

        next_page = response.xpath('//span[@class="next"]/a/@href').extract_first()
        index = next_page.rfind('=') + 1
        next_page_number = int(next_page[index :])

        if next_page is not None and next_page_number <= self.last_page:
            yield response.follow(url=next_page, callback=self.parseBookmarks)

    def getImage(self, response):
        """Insert image information into pipeline.

        Check if image is in an album.
        """
        image_url, image_format = os.path.splitext(response.url)
        num_of_images = response.meta.get('num_of_images')
        item = response.meta['item']
        item['image_urls'] = [response.url]

        if num_of_images:
            for image_num in range(1, int(num_of_images)):
                index = image_url.rfind('p') + 1
                orig_image_url = image_url[:index] + str(image_num) + image_format
                item['image_urls'].append(orig_image_url)
        return item

    def retryFormat(self, failure):
        """Try request again with png format."""
        response = failure.value.response
        if failure.check(HttpError):
            self.logger.warning('HttpError on %s', response.url)
            orig_image_url = os.path.splitext(response.url)[0] + '.png'
            self.logger.info("Attempting to download %s as %s.", response.url, orig_image_url)

            return scrapy.Request(url=orig_image_url,
                                  callback=self.getImage,
                                  headers=response.request.headers,
                                  meta=response.request.meta)
