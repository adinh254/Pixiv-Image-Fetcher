"""Initial Base spider

This module uses a spider to log in to Pixiv
using a provided form data and then redirects to the user bookmarks.
"""

import re
import scrapy
# from scrapy.http import HtmlResponse
# from scrapy.linkextractors import LinkExtractor

from .. import items

class BaseSpider(scrapy.Spider):
    """Initial spider to login to Pixiv page"""
    name = "login"

    allowed_domains = ['pixiv.net', 'i.pximg.net']

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

        id_pattern = re.compile(r'pixiv\.user\.id = "(\d+?)"')
        user_id = response.xpath('//head/script[contains(., "pixiv.user.id = ")]/text()') \
                                 .re(id_pattern)[0]

        self.logger.info("Login Successful!")
        return scrapy.Request(url=self.bookmarks_page, callback=self.parseBookmarks, 
                              meta={'user_id' : user_id})

    def parseBookmarks(self, response):
        """Gets all artist work and artist info in current bookmark page.

        Case if artist work is an album and contains multiple images.
        """

        img_link_pattern = re.compile(r'member.+?\d+')
        img_link_selectors = response.css('div.display_editable_works a._work').extract()

        artist_ids = response.xpath('//div[@class="display_editable_works"]//a/@data-user_id') \
                             .extract()

        for artist_work, artist_id in zip(img_link_selectors, artist_ids):
            if 'multiple' in artist_work:
                class_multiple = artist_work.replace('medium', 'manga')
                class_multiple = class_multiple.replace('amp;', '')
                album_link = img_link_pattern.search(class_multiple)[0]
                yield response.follow(url=album_link, callback=self.parseAlbum, 
                                      meta={
                                          'user_id' : response.meta['user_id'],
                                          'artist_id' : artist_id,
                                          }
                                     )
            else:
                img_link = img_link_pattern.search(artist_work)[0]
                img_link = img_link.replace('amp;', '')
                yield response.follow(url=img_link, callback=self.getImage,
                                      meta={
                                          'user_id' : response.meta['user_id'],
                                          'artist_id' : artist_id,
                                          }
                                     )

    def parseAlbum(self, response):
        """Obtain all image urls in current album."""

        index = response.url.rfind('=') + 1
        illust_id = response.url[index : -1]

        album_imgs = response.css('section.manga a::attr(href)').extract()
        for count, img_url in enumerate(album_imgs):
            yield response.follow(url=img_url, callback=self.getImage,
                                  meta={
                                      'img_num' : count + 1,
                                      'user_id' : response.meta['user_id'],
                                      'artist_id' : response.meta['artist_id'],
                                      'illust_id' : illust_id,
                                      'multiple' : True,
                                      }
                                 )

    def getImage(self, response):
        """Extract native image url from artist image page.

        Case if response has multiple images
        """

        item = items.BookmarksImage()
        multiple = response.meta.get('multiple')

        if multiple:
            illust_id = response.meta['illust_id']
            orig_url = response.xpath('//img/@src').extract_first()
            item['image_num'] = [response.meta['img_num']]

        else:
            pattern = re.compile('"original":"(.*?)"')
            pattern_url = response.xpath('//head/script[contains(., "urls")]/text()').re(pattern)[0]
            index = response.url.rfind('=') + 1
            illust_id = response.url[index: -1]
            orig_url = pattern_url.replace('\\', '')

        item['image_urls'] = [orig_url]
        item['referer'] = [response.url]
        item['user_id'] = [response.meta['user_id']]
        item['artist_id'] = [response.meta['artist_id']]
        item['illust_id'] = [illust_id]
        return item
