# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

"""Convert Image Urls to items

"""
import scrapy


class BookmarksImage(scrapy.Item):
    """Image information

    Downloaded image name format data
    """

    image_urls = scrapy.Field()
    referer = scrapy.Field()

    user_id = scrapy.Field()
    artist_id = scrapy.Field()
    illust_id = scrapy.Field()

class Tag(scrapy.Item):
    """Tag Information

    Extracted tag information
    """
    tag_name = scrapy.Field()
    tag_size = scrapy.Field()

    tag_link = scrapy.Field()
