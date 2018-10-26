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
    # Info
    image_urls = scrapy.Field()
    referer = scrapy.Field()

    #Format
    user_id = scrapy.Field()
    artist_id = scrapy.Field()
    illust_id = scrapy.Field()
    image_num = scrapy.Field()
