# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

"""Overload default file pipeline

Only saves jpgs and pngs
"""
import scrapy
from scrapy.pipelines.files import FilesPipeline
from scrapy.exceptions import DropItem

class PixivImagePipeline(FilesPipeline):

    def get_media_requests(self, item, info):
        try:
            return scrapy.Request(item['image_urls'][0], headers={'referer': item['referer'][0]})
        except TypeError:
            raise DropItem('Missing "image_url" in Response: %s;'
                           % item['referer'][0])
        except ValueError:
            raise DropItem('Image is an album')

    def item_completed(self, results, item, info):
        for success in results:
            if not success[0]:
                raise DropItem('Item contains no image')
        print('Image from %s downloaded!' % item['image_urls'][0])
        return item
